
import os
from cellblender_source_info import * 

    
if __name__ == '__main__':

    """
    Run this file from the command line to update the cellblender_id.py file.
    ID should be updated only when needed. No need to do this when a minor change that 
    does not change backwards compatibility is done. 
    Previous solution did update the SHA every time make was called and this then lead to 
    CellBLender offering updates for models every time a new version odf CellBlender was installed.  
    """

    id_file_name = "cellblender_id.py"
    identify_source_version(os.path.dirname(__file__),verbose=False)
    
    cb_id_statement = "cellblender_id = '" + cellblender_info['cellblender_source_sha1'] + "'\n"
    sha_file_name = os.path.join(os.path.dirname(__file__), id_file_name)
    rebuild = True
    if os.path.exists(sha_file_name):
        sha_file = open(sha_file_name, 'r')
        current_statement = sha_file.read()
        sha_file.close()
        if current_statement.strip() == cb_id_statement.strip():
            rebuild = False
    
    if rebuild:
        open(sha_file_name, 'w').write(cb_id_statement)

