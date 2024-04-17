# Learning to Grasp the Ungraspable with Emergent Extrinsic Dexterity

[//]: # (<div align="center">)

[//]: # (<font size=7>**Learning to Grasp the Ungraspable with Emergent Extrinsic Dexterity**</font>)

[Wenxuan Zhou](https://wenxuan-zhou.github.io/), [David Held](https://davheld.github.io/)

Robotics Institute, Carnegie Mellon University

Conference on Robot Learning (CoRL) 2022 (Oral)

[Paper](https://arxiv.org/abs/2211.01500)
| [Website](https://sites.google.com/view/grasp-ungraspable)
| [Real robot code](https://github.com/Wenxuan-Zhou/frankapy_env)

![intro.gif](imgs/intro.gif)

[//]: # (</div>)

In this paper, we build a system based on reinforcement learning that shows 
emergent extrinsic dexterity behavior with a simple gripper 
for the "Occluded Grasping" task. This repository contains the code for the
simulation environment of the Occluded Grasping task and RL
training and rollouts. The code for the real robot can be found in 
[a separate repository](https://github.com/Wenxuan-Zhou/frankapy_env).

This repository is built on top of [robosuite-benchmark](https://github.com/ARISE-Initiative/robosuite-benchmark). The simulation environment is based on [robosuite](https://robosuite.ai/) and the RL training related code 
is based on [rlkit](https://github.com/rail-berkeley/rlkit). As an overview of this repository, [ungraspable/robosuite_env](ungraspable%2Frobosuite_env)
defines the Occluded Grasping task. [ungraspable/rlkit_utils](ungraspable/rlkit_utils) defines helper functions to be used with rlkit.

Please feel free to contact us if you have any questions on the code or anything else related to our paper!

## Installation

Installation must be done on Linux / WSL.

Install Miniconda in your home directory using [this tutorial](https://dev.to/sfpear/miniconda-in-wsl-3642). You should see that `~/miniconda3` is a directory afterwards.

Download [MuJoCo 2.0](https://www.roboti.us/download/mujoco200_linux.zip) and extract the folder.

```bash
sudo apt-get install unzip
unzip mujoco200_linux.zip
```

After extracting the zip, move the extracted folder to `~/.mujoco/mujoco200`.

Download the [MuJoCo license file](https://www.roboti.us/file/mjkey.txt) and put it into `~/.mujoco/mjkey.txt`.

Add the following to your .bashrc, then source it.

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/.mujoco/mujoco200/bin
export PATH="$LD_LIBRARY_PATH:$PATH"
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libGLEW.so
```

Clone the current repository:
```bash
git clone --recursive https://github.com/HarrelsonJ/DeepRob_Ungraspable.git
cd DeepRob_Ungraspable
```

Edit the robosuite subrepo to change the versions of some packages.

* In [robosuite/requirements.txt](robosuite/requirements.txt), change the version of mujoco-py to 2.0.2.5
* In [robosuite/setup.py](robosuite/setup.py), change the version of mujoco-py to 2.0.2.5

Run the script [finish_install.sh](finish_install.sh) and go through the final install process. This will create a conda environment with the required packages. IMPORTANT: We require the exact version of robosuite and rlkit included in this directory.

Activate the conda environment.

```bash
conda activate ungraspable
```

Use [viskit](https://github.com/vitchyr/viskit) to visualize training log files. Do not install it in the above conda environment because there are compatibility issues.

## Usage
### Training
```bash
python train.py --ExpID 0000
```
The results will be saved under "./results" by default. During training, you can visualize current logged runs using [viskit](https://github.com/vitchyr/viskit).

To train the policy with a multi-grasp curriculum:
```bash
python train.py --adr_mode 0001_ADR_MultiGrasp --ExpID 0001 --goal_range use_threshold
```
"--adr_mode" specified an ADR configuration file under [ungraspable/rlkit_utils/adr_config](ungraspable%2Frlkit_utils%2Fadr_config).
Similarly, to train the policy with Automatic Domain Randomization over physical parameters:
```bash
python train.py --adr_mode 0002_ADR_physics --ExpID 0002
```
We include the results of the above training commands in [result/examples](results%2Fexamples), including the model and the training logs.
You may visualize the training curves of these examples using [viskit](https://github.com/vitchyr/viskit):
```bash
python your_viskit_folder/viskit/frontend.py ungraspable/results/examples
```

### Visualizing Rollouts
To visualize a trained policy with onscreen mujoco renderer:
```bash
python rollout.py --load_dir results/examples/Exp0000_OccludedGraspingSimEnv_tmp-0 --camera sideview --grasp_and_lift
```
Feel free to try out other checkpoints in the [result/examples](results%2Fexamples) folder.

## Citation
If you find this repository useful, please cite our paper:
```
@inproceedings{zhou2022ungraspable,
  title={Learning to Grasp the Ungraspable with Emergent Extrinsic Dexterity},
  author={Zhou, Wenxuan and Held, David},
  booktitle={Conference on Robot Learning (CoRL)},
  year={2022}
}
```
