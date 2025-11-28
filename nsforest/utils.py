
import pandas as pd
import argparse

# Simple argument parsing
def _parse_args(args, **kwargs): 
    parser = argparse.ArgumentParser(**kwargs, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", metavar = "cluster", type=str, 
                        help="parallelizing, one cluster at a time")
    return parser.parse_args()
  
def str_to_list(values): 
    """\
    Converting str representation of list to list

    Parameters
    ----------
    values: str representation of list
    
    Returns
    -------
    values: list
    """
    values = [val.replace("[", "").replace("]", "").replace(", ", ",").replace("'", "").replace('"', "").split(",") for val in values]
    return values

def prepare_markers(results, col_cluster, col_marker, output_folder = "", outputfilename_prefix = ""): 
    """\
    Converting marker_genes_csv to dictionary (clusterName: marker_genes)

    Parameters
    ----------
    filename
        csv with markers per cluster. 
    col_cluster
        Column name in file storing cell annotation.
    col_marker
        Column name in file storing markers.
    output_folder
        Output folder for missing genes. 
    outputfilename_prefix
        Prefix for missing genes file. 
    
    Returns
    -------
    marker_genes_dict: dictionary (cluster: list of markers)

    Creates files
    -------------
    {output_folder}{outputfilename_prefix}_not_found.csv: list of markers not found in anndata
    """
    # marker_genes_csv = pd.read_csv(filename) 
    not_found = []
    marker_genes_dict = {}
    # if markers are represented as list
    if "[" in list(results[col_marker])[0]: # "['NTNG1', 'EYA4']"
        marker_genes_dict = dict(zip(results[col_cluster], str_to_list(results[col_marker])))
    else: # 'NTNG1'\n'EYA4'
        for cluster, marker in zip(results[col_cluster], results[col_marker]): 
            if cluster not in marker_genes_dict: 
                marker_genes_dict[cluster] = [marker]
            else: 
                marker_genes_dict[cluster].append(marker)
    # removing duplicates
    for key in marker_genes_dict.keys(): 
        values = []
        for marker in marker_genes_dict[key]: 
            if marker not in values: values.append(marker)
        marker_genes_dict[key] = values
    # print out too
    if len(not_found) > 1: 
        print("WARNING: input markers not found in anndata\nMarkers:", not_found)
        # df = pd.DataFrame()
        # df[col_marker] = not_found
        # df.to_csv(output_folder + outputfilename_prefix + "_not_found.csv", index = False, header = False)

    return marker_genes_dict 

def make_safe_key(name: str) -> str:
    """
    Encodes a string to be safe for use as an HDF5 key (e.g., for adata.varm[...] or file paths).
    This avoids characters like '/' which are interpreted as group separators in HDF5.
    Reversible with `recover_original_key`.
    """
    return (
        name.replace("/", "_SLASH_")
            .replace("\\", "_BSLASH_")
            .replace(" ", "_SPACE_")
            .replace(":", "_COLON_")
            .replace(".", "_DOT_")
    )


def recover_original_key(safe_key: str) -> str:
    """
    Reverses the transformation applied by `make_safe_key`.
    """
    return (
        safe_key.replace("_SLASH_", "/")
                .replace("_BSLASH_", "\\")
                .replace("_SPACE_", " ")
                .replace("_COLON_", ":")
                .replace("_DOT_", ".")
    )


def store_key_mapping(adata, original_key: str, safe_key: str):
    """
    Stores a mapping between the original and safe keys in adata.uns['key_mappings'].
    """
    if "key_mappings" not in adata.uns:
        adata.uns["key_mappings"] = {}
    adata.uns["key_mappings"][original_key] = safe_key

def get_original_key(adata, safe_key: str) -> str:
    """
    Looks up the original cluster label from a safe key using adata.uns['key_mappings'].
    Falls back to the key itself if not found.
    """
    mapping = adata.uns.get("key_mappings", {})
    inv_map = {v: k for k, v in mapping.items()}
    return inv_map.get(safe_key, safe_key)

def reverse_key_list(adata, safe_keys: list) -> list:
    """
    Takes a list of safe keys and returns a list of original keys,
    using adata.uns["key_mappings"].
    """
    reverse_map = {}
    if "key_mappings" in adata.uns:
        reverse_map = {v: k for k, v in adata.uns["key_mappings"].items()}
    return [reverse_map.get(k, k) for k in safe_keys]

def build_varm_key(prefix: str, cluster_header: str) -> str:
    return f"{prefix}_{make_safe_key(cluster_header)}"
