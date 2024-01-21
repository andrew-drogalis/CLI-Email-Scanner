from os.path import isdir
from scanner.g_main import main
from scanner.full_system_scan import FullSystemScan

version = "v1.2"

if __name__ == '__main__':
    # Header
    print('','*'*60, '\n\n', f'---------- Pierpont Dispatch Email Scanner {version} ----------', '\n\n', '*'*60, '\n\n')

    if not isdir('S:/'):
        print('Please Connect to S: Drive and Restart\n\n')
    else:
        main()
        FullSystemScan()
        print('Scan Completed.\n\n')

    # Exit Pause
    input('Press Any Key to Exit... ')