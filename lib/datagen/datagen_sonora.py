# %%
import sys, os, glob
import numpy as np
import configparser

def process_data(cfile, data_dir, preserve=True):
        
    config = configparser.ConfigParser(allow_no_value = True)
    config.read_file(open(cfile, 'r'))
    
    for s in config:
        conf = config[s]

        loc_dir = os.path.join(conf['indir'], '')
        if not os.path.isabs(loc_dir):
            os.path.join(os.path.abspath(cfile).rsplit(os.sep, 1)[0], 
                            loc_dir)

        if not os.path.isabs(data_dir):
            data_dir = os.path.join(loc_dir, data_dir)
            train_dir = os.path.join(data_dir, 'train', '')
            valid_dir = os.path.join(data_dir, 'valid', '')
            test_dir  = os.path.join(data_dir, 'test' , '')

        num = os.listdir(loc_dir)
        ntest = max(np.floor(len(num) * 0.1), 1)
        nval  = max(np.floor(len(num) * 0.2), 1)
        ntr   = max(len(num) - ntest - nval,  1)

        if conf.getboolean('read_all') == True:
            files = glob.glob(data_dir + '/**/*.0', recursive = True) 
            # Runs through all binary files and reads them recursively if they are located in subfolders.
            # As of right now the parameters are included in the config file as a magic number, 
            # but they should be read by the given file and input later. 
            teststack = np.zeros((conf.getint('cases'), conf.getint('parameters')+1), dtype='f')
            validstack = np.zeros((conf.getint('cases'), conf.getint('parameters')+1), dtype='f')
            trainstack = np.zeros((conf.getint('cases'), conf.getint('parameters')+1), dtype='f')

            for n, file in enumerate(files):

                # Returns the 2D array as well if it was needed for something...
                datarr, datslice = read_file(conf, file)
                # If there has been x number of cases iterations then save file

                if n % conf.getint('cases') == 0:
                    # Save each individual array after m cases to its correct subdirectory.
                    np.save(train_dir + os.path.basename(file) + 'wav', trainstack)
                    np.save(valid_dir + os.path.basename(file) + 'wav', validstack)
                    np.save(test_dir + os.path.basename(file) + 'wav', teststack)

                    # Empty previous values
                    trainstack.fill(0)
                    validstack.fill(0)
                    teststack.fill(0)
                
                if   n < ntr:
                    trainstack[:n % conf.getint('cases')] = datslice
                elif n < ntr + nval:
                    validstack[:n % conf.getint('cases')] = datslice
                elif n < ntr + nval + ntest:
                    teststack[:n % conf.getint('cases')] = datslice
                
        # Test on one individual file
        elif conf.getboolean('read_all') == False:
            np.save(data_dir + conf['file'], read_file(conf['file']))
        
        print("The sonora data has been processed.")    
    return

def read_file(conf, file):
    """ 
    Parses SONORA data into a MARGE-legible format. 
    Runs information on per-file basis. 
    """
    with open(file, 'r') as f:
        print("Reading from file...")

        head = []
        for x in range(2):
            head += f.readline().strip().split()
        
        head = np.asarray(head)
        # Remove the label from the beginning of the file: Teff, grav (MKS), Y, f_rain, Kzz, [Fe/H], C/O, f_hole 
        params = head[:conf.getint('parameters')].astype(float)
        
        # microns | Flux (erg/cm^2/s/Hz)
        data_arr = np.loadtxt(file, dtype=f, skiprows=2, unpack=True)
        dat_slice = data_arr.T[:1].astype(float)
        
        # inputs at the beginning of the array.
        dat1d_whead = np.concatenate(params, dat_slice)
        f.close()

    return(data_arr, dat1d_whead)

# cfile = os.path.join(os.path.dirname(__file__), "SONORA.cfg")
# data_dir = os.path.join(os.getcwd(), "./spectra/sp_t200g10nc_m0.0/")
# process_data(cfile, data_dir)

# %%
