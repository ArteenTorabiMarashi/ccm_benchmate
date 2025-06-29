
import subprocess

import requests
import torch
from biotite.structure import sasa, distance, to_sequence, get_chains
from biotite.structure.io.pdb import PDBFile
from biotite.structure.alphabet import to_3di

from ccm_benchmate.structure.utils import *
from ccm_benchmate.containers.alphafold3.command import *


class Structure:
    def __init__(self, pdb=None, sequence=None):
        """
        constructor for Structure class
        :param pdb:
        :param sequence:
        :param predict:
        :param model:
        """
        self.pdb = pdb
        if pdb is not None:
            self.structure = PDBFile.read(self.pdb).get_structure()[0]
        if sequence is not None and self.pdb is None:
            self.sequence = sequence
        self.sasa = None
        self.embeddings = None
        self.seq_3di = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    #TODO check for multiple chains
    def download(self, id, source="PDB", destination=None, load_after_download=True):
        if source == "PDB":
            url = "http://files.rcsb.org/download/{}.pdb".format(id)
        elif source == "AFDB":
            url = "https://alphafold.ebi.ac.uk/files/AF-{}-F1-model_v4.pdb".format(id)
        else:
            raise NotImplementedError("We can only download structures from PDB or AFDB")

        download = requests.get(url, stream=True)
        download.raise_for_status()
        with open("{}/{}.pdb".format(destination, id), "wb") as f:
            f.write(download.content)

        self.pdb = "{}/{}.pdb".format(destination, id)

        if load_after_download:
            atom_array = PDBFile.read(self.pdb).get_structure()[0](self.pdb)
        self.structure = atom_array
        return self

    def calculate_embeddings(self, model="esm3", normalize=False):
        if model == "esm3":
            get_esm3_embeddings(self.pdb, normalize=normalize)
        else:
            raise NotImplementedError("We can only calculate embeddings from ESM3")

    def calculate_sasa(self, **kwargs):
        accessibility = sasa(self.structure, **kwargs)
        self.sasa = accessibility
        return self

    def get_3di(self):
        sequences, chain_starts = to_3di(self.structure)
        self.seq_3di = sequences
        return self

    def get_sequence(self):
        if hasattr(self, "structure"):
            sequence = to_sequence(self.structure)
            self.sequence = sequence
            return sequence
        else:
            raise ValueError("No structure loaded")
    def align(self, other, destination):
        if self.pdb is None or other.pdb is None:
            raise ValueError("Cannot align structures without a PDB")

        command = ["mustang", "-i", os.path.abspath(self.pdb), os.path.abspath(other.pdb), "-o",
                   os.path.abspath(destination), "-r", "ON"]
        process = subprocess.run(command)
        if process.returncode != 0:
            raise ValueError("There was an error aligning structures. See error below \n {}".format(process.stderr))

        aligned_pdb = os.path.abspath(destination + "results.pdb")
        rotation_file = os.path.abspath(destination + "results.rms_rot")
        html_report = os.path.abspath(destination + "results.html")
        return aligned_pdb, rotation_file, html_report

    def tm_score(self, other):
        pass

    #TODO implement AF2, and omegafold
    def predict(self, output_path, container, inference=True, pipeline=False, model="AF3"):
        if model != "AF3":
            raise NotImplementedError("We can only predict structures with AF3")
        generate_json(self.name, "apis", self.sequence, stoichiometry=1, fpath=output_path)
        os.makedirs(os.path.abspath(os.path.join(output_path, "af3_prediction")), exist_ok=True)
        command_dict["run_command"].format(pipeline, inference)
        command_dict["bind_mounts"][1] = os.path.abspath(output_path)
        command_dict["bind_mounts"][2]=os.path.abspath(os.path.join(output_path, "af3_prediction"))
        runner=ContainerRunner(container, command_dict)
        runner=runner.run()
        return runner

    def simulate(self, method="bioemu"):
        #TODO this will either run openmm or bioemu, the simulation runner is in the utils.
        pass

    def write(self, fpath):
        PDBFile.write(self.pdb, fpath)


class ProteinComplex(Structure):
    def __init__(self, pdb=None, sequence=None):
        super().__init__(pdb=pdb, sequence=sequence)
        self.chains=get_chains(self.structure)

    def _get_chain(self, chain_id):
        if type(chain_id) is int:
            chain_id = self.chains[chain_id]
        elif type(chain_id) is str:
            chain = self.structure[self.structure.chain_id==chain_id]
        else:
            raise ValueError("Chain ID must be an integer or a string representing the chain ID")
        return chain

    def get_chain_ids(self):
        return self.chains

    def contacts(self, chain_id1, chain_id2, cutoff=5.0, level="atom", measure="any"):
        """
        Get contacts between two chains in the structure.
        :param chain_id1:
        :param chain_id2:
        :param cutoff:
        :return:
        """
        chain1 = self._get_chain(chain_id1)
        chain2 = self._get_chain(chain_id2)
        contacts=[]
        for i in range(len(chain1)):
            for j in range(len(chain2)):
                if measure == "any":
                    dist = distance(chain1[i], chain2[j])
                elif measure=="CA":
                    if "CA" in chain1[i].atom_name and "CA" in chain2[j].atom_name:
                        dist = distance(chain1[i], chain2[j])
                    else:
                        continue
                if dist < cutoff:
                    if level == "atom":
                        contacts.append({chain_id1: i, chain_id2: j,
                                     "distance": dist})
                    elif level == "residue":
                        contacts.append({chain_id1: chain1[i].res_id, chain_id2: chain2[j].res_id,
                                     "distance": dist})

        return contacts


    def predict(self, output_path, container, inference=True, pipeline=False, model="AF3"):
        pass


