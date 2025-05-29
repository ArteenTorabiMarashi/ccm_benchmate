Install + Environment
```bash
git clone https://github.com/ccmbioinfo/ccm_benchmate.git

cd ccm_benchmate

intjob

mamba create --name benchmate_dev

mamba activate benchmate_dev

mamba install python=3.11 pip anaconda::jupyter 

mamba install -c conda-forge biotite

TMPDIR=/projects/dir/pip_cache pip install -r requirements_step1.txt

module load gcc/9.5.0
TMPDIR=/projects/dir/pip_cache pip install -r requirements_step2.txt

# Note, if planning on using containers through singularity, ensure you have run module load Singularity prior to launching python
```
