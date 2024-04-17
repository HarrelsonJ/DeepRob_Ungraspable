sudo apt-get update
sudo apt install libosmesa6-dev libgl1-mesa-glx libglfw3 libglew-dev libstdc++6
conda install -c conda-forge gcc=12.1.0

conda create --name ungraspable python=3.7.9

rm $HOME/miniconda3/envs/ungraspable/lib/libstdc++.so.6
cp $HOME/miniconda3/lib/libstdc++.so.6.0.32 $HOME/miniconda3/envs/ungraspable/lib
ln -s $HOME/miniconda3/envs/ungraspable/lib/libstdc++.so.6.0.32 $HOME/miniconda3/envs/ungraspable/lib/libstdc++.so.6

conda activate ungraspable
conda env update --file env.yml