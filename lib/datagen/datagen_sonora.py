# %%
import sys, os, glob
import numpy as np
import configparser

def process_data(cfile, data_dir, preserve=True):
        
    config = configparser.ConfigParser(allow_no_value = True)
    config.read_file(open(cfile, 'r'))
    
    for s in config:
        if s != 'DEFAULT':
            conf = config[s]
            # Using the config file, find the output directory. 
            output_dir = os.path.join(conf['outdir'], '')
            if not os.path.isabs(output_dir):
                output_dir = os.path.join(
                            os.path.abspath(cfile).rsplit(os.sep, 1)[0], 
                            output_dir)
                print(output_dir)

            if not os.path.isabs(data_dir):
                print(os.path.join(loc_dir, data_dir))
            
            print(os.path.join(output_dir, 'train', ''))
            try:
                train_dir = os.path.join(output_dir, 'train', '')
                print(train_dir)
            except FileNotFoundError:
                print("Training subdirectory not found. Creating one.")
                os.mkdir(os.path.join(output_dir, 'train', ''))
                train_dir = os.path.join(output_dir, 'train', '')
            try:
                valid_dir = os.path.join(output_dir, 'valid', '')
                print(valid_dir)
            except FileNotFoundError:
                print("Validation subdirectory not found. Creating one.")
                os.mkdir(os.path.join(output_dir, 'valid', ''))
                valid_dir = os.path.join(output_dir, 'valid', '')
            
            try:
                test_dir  = os.path.join(output_dir, 'test' , '')
                print(test_dir)
            except FileNotFoundError:
                print("Test subdirectory not found. Creating one.")
                os.mkdir(os.path.join(output_dir, 'test' , ''))
                test_dir  = os.path.join(output_dir, 'test' , '')
            
            finally:
                cases = conf['cases']
                print("Case number: " + cases)
                num = os.listdir(data_dir)
                ntest = max(np.floor(len(num) * 0.1), 1)
                nval  = max(np.floor(len(num) * 0.2), 1)
                ntr   = max(len(num) - ntest - nval,  1)
                
                if conf.getboolean('read_all') == True:
                    files = glob.glob(data_dir + '/*.0') 
                    print("Reading from files...")
                    # Runs through all binary files and reads them. All binaries should be in the spectra/ directory 
                    # without any container directories.
                    # As of right now the parameters are included in the config file as a magic number, 
                    # but they should be read by the given file and input later. 

                    teststack = np.zeros((conf.getint('cases'), conf.getint('slice_param')), dtype='f')
                    validstack = np.zeros((conf.getint('cases'), conf.getint('slice_param')), dtype='f')
                    trainstack = np.zeros((conf.getint('cases'), conf.getint('slice_param')), dtype='f')
            
                    for n, file in enumerate(files):
                        print(file)
                        # Returns the 2D array as well if it was needed for something...
                        datarr, datslice = read_file(conf, file)
                        if n % conf.getint('cases') == 0 and n != 0:
                            # Save each individual array after m cases to its correct subdirectory.
                            np.save(train_dir + os.path.basename(file) + n, trainstack)
                            np.save(valid_dir + os.path.basename(file) + n, validstack)
                            np.save(test_dir + os.path.basename(file) + n, teststack)

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
                        
        # If there has been x number of cases iterations then save file
        # The data_dir will be where the inputs start. 
        # Separate the outputs into three groups: train, validate, and test.
        # Take every file and read it through to parse the inputs and the outputs. 
        # Stack them on top of each other in a 2D array that is size(cases, spectra). 
        # After a specified amount of cases read, save the 2d array, delete whatever is being stored in memory, and start again. 

    return

def read_file(conf, file):
    """ 
    Parses SONORA data into a MARGE-legible format. 
    Runs information on per-file basis. 
    """
    with open(file, 'r') as f:

        head = []
        for x in range(2):
            head += f.readline().strip().split()
        
        head = np.asarray(head)
        # Remove the label from the beginning of the file: Teff, grav (MKS), Y, f_rain, Kzz, [Fe/H], C/O, f_hole 
        params = head[:conf.getint('parameters')].astype(float)
        
        # microns | Flux (erg/cm^2/s/Hz)
        data_arr = np.loadtxt(file, dtype='f', skiprows=2, unpack=True)
        dat_slice = data_arr.T[:1].astype(float)
        
        # inputs at the beginning of the array.
        dat1d_whead = np.append(params, dat_slice)
        print(dat1d_whead)
        f.close()

    return(data_arr, dat1d_whead)

cfile = os.path.join(os.getcwd(), "SONORA.cfg")
data_dir = os.path.join(os.getcwd(), "./spectra/")
process_data(cfile, data_dir)

# %%
