import numpy as np
from collections import OrderedDict
from robosuite.environments.manipulation.manipulation_env import ManipulationEnv
from robosuite.models.objects import BoxObject
from robosuite.models.tasks import ManipulationTask
from robosuite.utils.mjcf_utils import CustomMaterial
from robosuite.utils.observables import Observable, sensor
from robosuite.utils.placement_samplers import UniformRandomSampler

from ungraspable.robosuite_env.bin_arena import BinArena
from ungraspable.robosuite_env.single_arm import SingleArm


class BaseEnv(ManipulationEnv):
    """
    Modified based on robosuite.environments.manipulation.lift

    This class corresponds to the lifting task for a single robot arm.

    Args:
        robots (str or list of str): Specification for specific robot arm(s) to be instantiated within this env
            (e.g: "Sawyer" would generate one arm; ["Panda", "Panda", "Sawyer"] would generate three robot arms)
            Note: Must be a single single-arm robot!

        initial_qpos (array): Robot initial joint configuration

        env_configuration (str): Specifies how to position the robots within the environment (default is "default").
            For most single arm environments, this argument has no impact on the robot setup.

        controller_configs (str or list of dict): If set, contains relevant controller parameters for creating a
            custom controller. Else, uses the default controller for this specific task. Should either be single
            dict if same controller is to be used for all robots or else it should be a list of the same length as
            "robots" param

        gripper_types (str or list of str): type of gripper, used to instantiate
            gripper models from gripper factory. Default is "default", which is the default grippers(s) associated
            with the robot(s) the 'robots' specification. None removes the gripper, and any other (valid) model
            overrides the default gripper. Should either be single str if same gripper type is to be used for all
            robots or else it should be a list of the same length as "robots" param

        initialization_noise (dict or list of dict): Dict containing the initialization noise parameters.
            The expected keys and corresponding value types are specified below:

            :`'magnitude'`: The scale factor of uni-variate random noise applied to each of a robot's given initial
                joint positions. Setting this value to `None` or 0.0 results in no noise being applied.
                If "gaussian" type of noise is applied then this magnitude scales the standard deviation applied,
                If "uniform" type of noise is applied then this magnitude sets the bounds of the sampling range
            :`'type'`: Type of noise to apply. Can either specify "gaussian" or "uniform"

            Should either be single dict if same noise value is to be used for all robots or else it should be a
            list of the same length as "robots" param

            :Note: Specifying "default" will automatically use the default noise settings.
                Specifying None will automatically create the required dict with "magnitude" set to 0.0.

        table_full_size (3-tuple): x, y, and z dimensions of the table.

        table_friction (3-tuple): the three mujoco friction parameters for
            the table.

        table_offset (3-tuple): x, y, and z location of the table top with respect to the robot base.

        use_camera_obs (bool): if True, every observation includes rendered image(s)

        use_object_obs (bool): if True, include object (cube) information in
            the observation.

        reward_scale (None or float): Scales the normalized reward function by the amount specified.
            If None, environment reward remains unnormalized

        reward_shaping (bool): if True, use dense rewards.

        placement_initializer (ObjectPositionSampler): if provided, will
            be used to place objects on every reset, else a UniformRandomSampler
            is used by default.

        has_renderer (bool): If true, render the simulation state in
            a viewer instead of headless mode.

        has_offscreen_renderer (bool): True if using off-screen rendering

        render_camera (str): Name of camera to render if `has_renderer` is True. Setting this value to 'None'
            will result in the default angle being applied, which is useful as it can be dragged / panned by
            the user using the mouse

        render_collision_mesh (bool): True if rendering collision meshes in camera. False otherwise.

        render_visual_mesh (bool): True if rendering visual meshes in camera. False otherwise.

        render_gpu_device_id (int): corresponds to the GPU device id to use for offscreen rendering.
            Defaults to -1, in which case the device will be inferred from environment variables
            (GPUS or CUDA_VISIBLE_DEVICES).

        control_freq (float): how many control signals to receive in every second. This sets the amount of
            simulation time that passes between every action input.

        horizon (int): Every episode lasts for exactly @horizon timesteps.

        ignore_done (bool): True if never terminating the environment (ignore @horizon).

        hard_reset (bool): If True, re-loads model, sim, and render object upon a reset call, else,
            only calls sim.reset and resets all robosuite-internal variables

        camera_names (str or list of str): name of camera to be rendered. Should either be single str if
            same name is to be used for all cameras' rendering or else it should be a list of cameras to render.

            :Note: At least one camera must be specified if @use_camera_obs is True.

            :Note: To render all robots' cameras of a certain type (e.g.: "robotview" or "eye_in_hand"), use the
                convention "all-{name}" (e.g.: "all-robotview") to automatically render all camera images from each
                robot's camera list).

        camera_heights (int or list of int): height of camera frame. Should either be single int if
            same height is to be used for all cameras' frames or else it should be a list of the same length as
            "camera names" param.

        camera_widths (int or list of int): width of camera frame. Should either be single int if
            same width is to be used for all cameras' frames or else it should be a list of the same length as
            "camera names" param.

        camera_depths (bool or list of bool): True if rendering RGB-D, and RGB otherwise. Should either be single
            bool if same depth setting is to be used for all cameras or else it should be a list of the same length as
            "camera names" param.

        camera_segmentations (None or str or list of str or list of list of str): Camera segmentation(s) to use
            for each camera. Valid options are:

                `None`: no segmentation sensor used
                `'instance'`: segmentation at the class-instance level
                `'class'`: segmentation at the class level
                `'element'`: segmentation at the per-geom level

            If not None, multiple types of segmentations can be specified. A [list of str / str or None] specifies
            [multiple / a single] segmentation(s) to use for all cameras. A list of list of str specifies per-camera
            segmentation setting(s) to use.

        adaptive (bool): If true, include ADR parameters in the observation based on additional_obs_keys.

        additional_obs_keys (list): Additional parameters to be included in the observation.

    Raises:
        AssertionError: [Invalid number of robots specified]
    """

    def __init__(
        self,
        robots,
        initial_qpos=None,
        env_configuration="default",
        controller_configs=None,
        gripper_types="default",
        occlusion_type="ground",
        use_random_occlusion=False,
        initialization_noise="default",
        table_full_size=(0.45, 0.54, 0.107),
        table_friction=(0.3, 5e-3, 1e-4),
        table_offset=(0.5, 0, 0.065),
        use_camera_obs=True,
        use_object_obs=True,
        reward_scale=1.0,
        reward_shaping=False,
        placement_initializer=None,
        has_renderer=False,
        has_offscreen_renderer=True,
        render_camera="frontview",
        render_collision_mesh=False,
        render_visual_mesh=True,
        render_gpu_device_id=-1,
        control_freq=20,
        horizon=1000,
        ignore_done=False,
        hard_reset=True,
        camera_names="agentview",
        camera_heights=256,
        camera_widths=256,
        camera_depths=False,
        camera_segmentations=None,      # {None, instance, class, element}
        adaptive=False,
        additional_obs_keys=None,
        **kwargs
    ):
        if initial_qpos is None:
            self.initial_qpos = np.array([0, 0.15, 0, -2.44, 0, 2.62, -7.84e-01])
        else:
            self.initial_qpos = initial_qpos

        # settings for table top
        self.table_full_size = np.array(table_full_size)
        self.table_friction = np.array(table_friction)
        self.table_offset = np.array(table_offset)

        # reward configuration
        self.reward_scale = reward_scale
        self.reward_shaping = reward_shaping

        # whether to use ground-truth object states
        self.use_object_obs = use_object_obs

        # object placement initializer
        self.placement_initializer = placement_initializer

        # Additional Parameters for ADR
        self.object_initial_pose_y_min = 0
        self.object_initial_pose_y_max = 0
        self.object_pos_noise = 0
        self.object_ori_noise = 0
        self.table_offset_x_min = 0.5
        self.table_offset_x_max = 0.5
        self.table_offset_z_min = 0.065
        self.table_offset_z_max = 0.065
        
        self.use_random_occlusion = use_random_occlusion
        self.occlusion_type = occlusion_type
        self.init_box_size()
        self.object_density_min = 86.
        self.object_density_max = 86.
        self.object_density_val = 86.

        self.table_friction_min = 0.3
        self.table_friction_max = 0.3
        self.table_friction_val = 0.3
        self.gripper_friction_min = 3
        self.gripper_friction_max = 3
        self.gripper_friction_val = 3

        self.controller_max_translation_max = 0.03
        self.controller_max_translation_min = 0.03
        self.controller_max_rotation_max = 0.2
        self.controller_max_rotation_min = 0.2

        self.additional_obs_keys = additional_obs_keys if adaptive and additional_obs_keys else None

        super().__init__(
            robots=robots,
            env_configuration=env_configuration,
            controller_configs=controller_configs,
            mount_types="default",
            gripper_types=gripper_types,
            initialization_noise=initialization_noise,
            use_camera_obs=use_camera_obs,
            has_renderer=has_renderer,
            has_offscreen_renderer=has_offscreen_renderer,
            render_camera=render_camera,
            render_collision_mesh=render_collision_mesh,
            render_visual_mesh=render_visual_mesh,
            render_gpu_device_id=render_gpu_device_id,
            control_freq=control_freq,
            horizon=horizon,
            ignore_done=ignore_done,
            hard_reset=hard_reset,
            camera_names=camera_names,
            camera_heights=camera_heights,
            camera_widths=camera_widths,
            camera_depths=camera_depths,
            camera_segmentations=camera_segmentations,
        )
    
    def init_box_size(self):
        if self.occlusion_type == 'ground':
            self.object_size_x_min = 0.15
            self.object_size_x_max = 0.15
            self.object_size_x_val = 0.15
            self.object_size_y_min = 0.20
            self.object_size_y_max = 0.20
            self.object_size_y_val = 0.20
            self.object_size_z_min = 0.05
            self.object_size_z_max = 0.05
            self.object_size_z_val = 0.05
            self.object_to_wall_dist_min = 0
            self.object_to_wall_dist_max = 0
        else:
            self.object_size_x_min = 0.06
            self.object_size_x_max = 0.06
            self.object_size_x_val = 0.06
            self.object_size_y_min = 0.20
            self.object_size_y_max = 0.20
            self.object_size_y_val = 0.20
            self.object_size_z_min = 0.06
            self.object_size_z_max = 0.06
            self.object_size_z_val = 0.06
            
            if self.occlusion_type == 'side':
                self.object_to_wall_dist_min = 0
                self.object_to_wall_dist_max = 0
            else:
                self.object_to_wall_dist_min = 0.05
                self.object_to_wall_dist_max = 0.1

    def _load_model(self):
        """
        Loads an xml model, puts it in self.model
        """
        super()._load_model()
        
        if self.use_random_occlusion:
            self.occlusion_type = np.random.choice(['ground', 'side', 'none'])
        
        # print('Occlusion type', self.occlusion_type)
        
        self.init_box_size()

        if 'max_translation' in self.robots[0].controller_config:
            self.robots[0].controller_config['max_translation'] = np.random.uniform(self.controller_max_translation_min,
                                                                                    self.controller_max_translation_max)
        if 'max_rotation' in self.robots[0].controller_config:
            self.robots[0].controller_config['max_rotation'] = np.random.uniform(self.controller_max_rotation_min,
                                                                                 self.controller_max_rotation_max)

        # load model for table top workspace
        self.table_friction_val = np.random.uniform(self.table_friction_min, self.table_friction_max)
        self.table_friction[0] = self.table_friction_val
        self.table_offset[0] = np.random.uniform(low=self.table_offset_x_min,
                                                 high=self.table_offset_x_max)
        self.table_offset[2] = np.random.uniform(low=self.table_offset_z_min,
                                                 high=self.table_offset_z_max)
        mujoco_arena = BinArena(bin_pos=self.table_offset,
                                bin_full_size=self.table_full_size,
                                bin_friction=self.table_friction,
                                hidden_walls="")

        # initialize objects of interest
        tex_attrib = {
            "type": "cube",
        }
        mat_attrib = {
            "texrepeat": "1 1",
            "specular": "0.4",
            "shininess": "0.1",
        }
        
        if self.occlusion_type == 'ground':
            obj_texture = CustomMaterial(
                texture="WoodRed",
                tex_name="redwood",
                mat_name="redwood_mat",
                tex_attrib=tex_attrib,
                mat_attrib=mat_attrib,
            )
        else:
            obj_texture = CustomMaterial(
                texture="WoodBlue",
                tex_name="bluewood",
                mat_name="bluewood_mat",
                tex_attrib=tex_attrib,
                mat_attrib=mat_attrib,
            )

        self.object_size_x_val = np.random.uniform(self.object_size_x_min, self.object_size_x_max)
        self.object_size_y_val = np.random.uniform(self.object_size_y_min, self.object_size_y_max)
        self.object_size_z_val = np.random.uniform(self.object_size_z_min, self.object_size_z_max)
        self.object_density_val = np.random.randint(self.object_density_min, self.object_density_max + 1)

        self.cube = BoxObject(
            name="cube",
            size_min=[self.object_size_x_val / 2, self.object_size_y_val / 2, self.object_size_z_val / 2],
            # [0.015, 0.015, 0.015],
            size_max=[self.object_size_x_val / 2, self.object_size_y_val / 2, self.object_size_z_val / 2],
            # [0.018, 0.018, 0.018])
            rgba=[1, 0, 0, 1],
            material=obj_texture,
            density=self.object_density_val,
        )

        # Create placement initializer
        xpos_max = self.table_full_size[0] / 2 - self.cube.size[0]
        self.placement_initializer = UniformRandomSampler(
            name="ObjectSampler",
            mujoco_objects=self.cube,
            x_range=[xpos_max - self.object_to_wall_dist_max, xpos_max - self.object_to_wall_dist_min],
            y_range=[self.object_initial_pose_y_min, self.object_initial_pose_y_max],
            rotation=0,
            ensure_object_boundary_in_range=False,  # Problematic
            ensure_valid_placement=False,
            reference_pos=self.table_offset,
            z_offset=0,
        )

        # task includes arena, robot, and objects of interest
        self.model = ManipulationTask(
            mujoco_arena=mujoco_arena,
            mujoco_robots=[robot.robot_model for robot in self.robots],
            mujoco_objects=self.cube,
        )

    def _setup_references(self):
        """
        Sets up references to important components. A reference is typically an
        index or a list of indices that point to the corresponding elements
        in a flatten array, which is how MuJoCo stores physical simulation data.
        """
        super()._setup_references()

        # Additional object references from this env
        self.cube_body_id = self.sim.model.body_name2id(self.cube.root_body)

    def _setup_observables(self):
        """
        Sets up observables to be used for this environment. Creates object-based observables if enabled

        Returns:
            OrderedDict: Dictionary mapping observable names to its corresponding Observable object
        """
        observables = super()._setup_observables()

        # low-level object information
        if self.use_object_obs:
            # Get robot prefix and define observables modality
            pf = self.robots[0].robot_model.naming_prefix
            modality = "object"

            # cube-related observables
            @sensor(modality=modality)
            def cube_pos(obs_cache):
                return np.array(self.sim.data.body_xpos[self.cube_body_id])

            @sensor(modality=modality)
            def cube_quat(obs_cache):
                return np.array(self.sim.data.body_xquat[self.cube_body_id])

            sensors = [cube_pos, cube_quat]
            names = [s.__name__ for s in sensors]

            # Create observables
            for name, s in zip(names, sensors):
                observables[name] = Observable(
                    name=name,
                    sensor=s,
                    sampling_rate=self.control_freq,
                )

        return observables

    def _reset(self):
        super().reset()
    
    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()

        # Reset all object positions using initializer sampler if we're not directly loading from an xml
        if not self.deterministic_reset:

            # Sample from the placement initializer for all objects
            object_placements = self.placement_initializer.sample()

            # Loop through all objects and reset their positions
            for obj_pos, obj_quat, obj in object_placements.values():
                self.sim.data.set_joint_qpos(obj.joints[0], np.concatenate([np.array(obj_pos), np.array(obj_quat)]))

    def _load_robots(self):
        gripper_friction = np.array([3, 0.015, 0.0003])
        self.gripper_friction_val = np.random.uniform(self.gripper_friction_min, self.gripper_friction_max)
        gripper_friction[0] = self.gripper_friction_val
        self.robots[0] = SingleArm(robot_type=self.robot_names[0], idn=0, control_gripper=False,
                                   initial_qpos=self.initial_qpos, gripper_friction=gripper_friction,
                                   **self.robot_configs[0])
        self.robots[0].load_model()
