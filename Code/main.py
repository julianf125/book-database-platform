import argparse
from goodreads import fix_match, check_and_fetch_ids, update_all_ids

def main():
    parser = argparse.ArgumentParser(description='Command line tool for Goodreads and Notion integration.')
    parser.add_argument('--fix_match', action='store_true', help='Run the fix_match function')
    parser.add_argument('--get_new', action='store_true', help='Run the check_and_fetch_ids function')
    parser.add_argument('--update', action='store_true', help='Run the update_all_ids function')
    args = parser.parse_args()
    
    if args.fix_match:
        fix_match()
    elif args.get_new:
        check_and_fetch_ids()
    elif args.update:
        update_all_ids()
    else:
        print("No valid command provided. Use --help for usage information.")

if __name__ == "__main__":
    main()
