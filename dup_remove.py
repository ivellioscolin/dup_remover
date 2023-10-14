import os, sys, datetime, pathlib, hashlib, threading, argparse

THREAD_NUMBER = 16
HASH_METHOD = 'md5' #md5, sha1, sha256, sha512, blake2b, blake2s

def prepare_file_list(root_path):
    return list(filter(lambda x: x.is_file(), pathlib.Path(root_path).rglob("*")))

def hash_one_file(file):
    with open(file, "rb") as f:
        digest = hashlib.file_digest(f, HASH_METHOD)
    return digest.hexdigest()

def hash_files(file_list, result_list, tid):
    for f in file_list:
        result_list[tid][str(f)] = hash_one_file(str(f))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove duplicated files by hash in given directory recursively', exit_on_error=False)
    parser.add_argument('dir', metavar='dir', help='Directory to recursively process')
    parser.add_argument('-t', metavar='threads', help='Thread number, default: 16', default = THREAD_NUMBER)
    parser.add_argument('-a', help='Auto-mode, always keep the 1st file and remove others', action="store_true")
    parser.add_argument('-d', help='dry-run, skip the actual deletion', action="store_true")

    try:
        args = parser.parse_args()
    except SystemExit:
        #print(parser.format_help())
        sys.exit(0)

    if(not os.path.isdir(args.dir)):
        print("%s is not a path" %(args.dir))
        sys.exit(0)

    try:
        threads = int(args.t)
        if (threads <= 0):
            threads = THREAD_NUMBER
            print("Invalid threads number, use default %d" %(THREAD_NUMBER))
    except:
        threads = THREAD_NUMBER
        print("Invalid threads number, use default %d" %(THREAD_NUMBER))

    auto_remove = args.a
    dry_run = args.d

    file_list = []
    t_list = []
    result_list = []

    ts1 = datetime.datetime.now()
    file_list = prepare_file_list(args.dir)

    group_size = len(file_list) // threads + (len(file_list) % threads > 0)
    print("Processing %d files in %d threads, %d files/group" %(len(file_list), threads, group_size))
    for tid in range(threads):
        result_list.append({})
        t = threading.Thread(target=hash_files, args=(file_list[tid * group_size : (tid + 1) * group_size], result_list, tid))
        t.start()
        t_list.append(t)

    for t in t_list:
        t.join()
    
    ts2 = datetime.datetime.now()
    print( "Done file hashing in", str(ts2 - ts1))

    results = {}
    for d in result_list:
        results.update(d)

    results_rev = {}
    for key, value in results.items():
        results_rev.setdefault(value, set()).add(key)

    if (dry_run):
        for key, values in results_rev.items():
            if len(values) > 1:
                print(values)
    else:
        for key, values in results_rev.items():
            if len(values) > 1:
                if auto_remove:
                    for f in list(values):
                        print('%d: %s' %(list(values).index(f),f))
                    for fi in range(1, len(list(values))):
                        print('  Deleting %s' %(list(values)[fi]))
                        os.system('attrib -R "%s"' %(list(values)[fi]))
                        os.remove(list(values)[fi])
                else:
                    for f in list(values):
                        print('  %d: %s' %(list(values).index(f),f))
                    choice = None
                    while True:
                        try:
                            raw_input = input('Duplicated files found. Which to keep (s to skip)? ')
                            choice = int(raw_input)
                            assert 0 <= choice < len(values) 
                        except ValueError:
                            skip = str(raw_input)
                            if skip.lower() == 's'.lower():
                                print('  Skipping')
                                break
                            else:
                                print('  Unknown choice')
                        except AssertionError:
                            print('  Invalid file index')
                        else:
                            break
                    if choice != None:
                        for f in list(values):
                            if choice != list(values).index(f):
                                print('  Deleting %s' %(f))
                                os.remove(f)