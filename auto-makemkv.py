from makemkv import MakeMKV #pip install makemkv
import PTN #pip install parse-torrent-title
import requests #pip install requests
import os
import sys


api_key = "your_tmdb_api_key"


lib_path = "/your/library/source/path"


dest_path = "/your/library/destination/path"


class Media: #class to store media info
    def __init__(self, path, type, title, year, season, quality, encoder):
        self.path = path
        self.type = type
        self.title = title
        self.year = year
        self.season = season
        self.quality = quality
        self.encoder = encoder


class SkipDisc(Exception): #exception to skip disc at any time during processing
    pass


def skip_disc(): #function to skip disc
    print("Skipping Disc...")
    raise SkipDisc


def check_auto(): #check if auto parameter is passed
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        return True
    else:
        return False


def get_lib_path(lib_path): #get library source path
    if check_auto():
        return lib_path
    else:
        while True:
            lib_path = input("Enter the library path to be scanned: ")
            if os.path.isdir(lib_path):
                break
            else:
                print("Invalid path. Please try again.")
        return lib_path


def get_dest_path(dest_path): #get library destination path
    if check_auto():
        return dest_path
    else:
        while True:
            dest_path = input("Enter the destination path for the media: ")
            if os.path.isdir(dest_path):
                break
            else:
                print("Invalid path. Please try again.")
        return dest_path


def get_skip_logged(): #check if user wants to skip logged discs
    if not os.path.exists("makemkv_log.txt"):
        with open("makemkv_log.txt", "a"):
            pass
    if check_auto():
        return True
    while True:
        skip_input = input("Skip logged discs? Log can be found in makemkv_log.txt. (y/n): ")
        if skip_input.lower() == "y":
            skip_logged = True
            break
        elif skip_input.lower() == "n":
            skip_logged = False
            break
        else:
            print("Invalid input. Please try again.")
    return skip_logged


def find_discs(lib_path): #create list of discs to be processed, in BDMV, VIDEO_TS, or .iso format
    disc_list = []
    for folder_path, _, file_names in os.walk(lib_path):
        if os.path.basename(folder_path) == 'BDMV' or os.path.basename(folder_path) == 'VIDEO_TS':
            disc_list.append(folder_path)
        
        for file_name in file_names:
            if file_name.endswith('.iso'):
                file_path = os.path.join(folder_path, file_name)
                disc_list.append(file_path)
    return disc_list


def get_disc_parent(disc_path, lib_path): #get the disc parent foldername, for torrent title parsing
    curr_path = disc_path
    while curr_path != lib_path:
        curr_path, curr_name = os.path.split(curr_path)
    return curr_name


def parse_disc(disc_parent): #parse torrent title for media info
    disc_info = PTN.parse(disc_parent)
    return disc_info


def make_media(disc_info, disc_path): #create media object from disc path and parsed info
    media = Media(disc_path, "", "", "", "", "", "")
    if "title" in disc_info:
        media.title = disc_info["title"]
    if "year" in disc_info:
        media.year = disc_info["year"]
    if "season" in disc_info:
        media.season = disc_info["season"]
    if "quality" in disc_info:
        media.quality = disc_info["quality"]
    if "encoder" in disc_info:
        media.encoder = disc_info["encoder"]
    return media


def print_found_media(media): #print found disc info, and prompt user to edit or skip
    try:
        print()
        print("*" * 11)
        print("Disc Found!")
        print(f"Path: {media.path}")
        print((f"Title: {media.title}"))
        if media.season != "":
            print(f"Season: {media.season}")
        print(f"Year: {media.year}")
        print("*" * 11)
        if check_auto():
            return
        while True:
            edit_input = input("Input 'e' to edit search parameters, 's' to skip this disc, enter to continue: ")
            if edit_input.lower() == "e":
                media = edit_media(media)
                break
            elif edit_input.lower() == "":
                break
            elif edit_input.lower() == "s":
                skip_disc()
            else:
                print("Invalid input. Please try again.")
    except SkipDisc:
        raise


def edit_media(media): #allow user to manually edit media info
    try:
        while True:
            title_input = input("Title: ")
            if (media.season != ""):
                season_input = input("Season: ")
            while True:
                year_input = input("Year: ")
                if year_input.isdigit() or year_input == "":
                    break
                else:
                    print("Invalid year input. Please enter an integer.")
            while True:
                cont_input = input("Press enter to continue, 'e' to edit, or 's' to skip this disc:")
                if cont_input == "":
                    break
                elif cont_input == "s":
                    skip_disc()
                elif cont_input == "e":
                    break
            if cont_input == "":
                break
        media.title = title_input
        if (media.season != ""):
            media.season = season_input
        media.year = year_input
        
    except SkipDisc:
        raise


def search_tmdb(media): #send api search request to tmdb, return filtered results excluding entries with no title
    search_endpoint = f'https://api.themoviedb.org/3/search/multi?api_key={api_key}&query='
    response = requests.get(search_endpoint + media.title)
    results = response.json()['results']
    filtered_results = [result for result in results if 'title' in result]
    return filtered_results


def find_match(results, media): #check if any results match the media year, return index of matched result
    i = 0
    matched = False
    for result in results:
        if str(media.year) in result['release_date']:
            print("*" * 11)
            print("Match found!")
            print(f"{result['title']} ({result['release_date']})")
            print("*" * 11)
            matched = True
            break
        i=i+1
    if matched == True:
        if check_auto():
            return matched, i
        while True:
            okay_match = input("Press enter to use this match, or 'a' to show all results: ")
            if okay_match == "":
                break
            elif okay_match == "a":
                matched = False
                break
            else:
                print("Invalid input. Please try again.")
    return matched, i


def print_all_results(results): #print all results from tmdb search
    print("*" * 11)
    if len(results) == 0:
        return
    else:
        i = 0
        for result in results:
            if 'release_date' in result:
                release_date = result['release_date']
            else:
                release_date = "N/A"
            
            print(f"[{i+1}]. {result['title']} ({release_date})")
            i=i+1
    print("*" * 11)


def get_results_choice(results, media): #prompt user to select a result, or edit search query
    custom = False
    choice = 0
    try:
        if len(results) == 0:
            if check_auto():
                skip_disc()
            choice = input("No results found. Enter 'e' to edit search query, 'c' to use custom fields, or 's' to skip this disc: ")
        else:
            if check_auto():
                choice = 0
                return custom, choice
            choice = input("Please enter the number of the correct match, 'e' to edit search query, 'c' to use a custom name/year, or 's' to skip this disc: ")
        while True:
            if choice == "e":
                media = edit_media(media)
                results = search_tmdb(media)
                matched, i = find_match(results, media)
                if matched == False:
                    print_all_results(results)
                    custom, choice = get_results_choice(results, media)
                    break
            elif choice == "c":
                media = edit_media(media)
                custom = True
                break
            elif choice == "s":
                skip_disc()
            elif len(results) > 0 and choice.isdigit() and int(choice) <= len(results) and int(choice) > 0:
                choice = int(choice) - 1
                break
            else:
                print("Invalid input. Please try again.")
        return custom, choice
    except SkipDisc:
        raise


def edit_media_choice(media, choice, results): #edit media info based on user choice
    media.title = results[choice]['title']
    if 'release_date' in results[choice]:
        media.year = results[choice]['release_date']


def makemkv_folder(media, dest_path): #create folder for makemkv output
    try:
        folder_string = f"{media.title} ({media.year[0:4]})"
        folder_path = os.path.join(dest_path, folder_string)
        while True:
            try:
                os.mkdir(folder_path)
                break
            except PermissionError:
                if check_auto():
                    skip_disc()
                cont_input = input("Could not write to destination folder. Check your permissions, and press enter to try again, or 's' to skip this disc: ")
                while True:
                    if cont_input == "":
                        break
                    elif cont_input.lower() == "s":
                        skip_disc()
                    else:
                        print("Invalid input. Please try again.")
            except FileExistsError:
                if check_auto():
                    skip_disc()
                print("Folder already exists.")
                break
        return folder_path, folder_string
    except SkipDisc:
        raise    


def mkvgen(media, folder_path): #generate mkv file
    try:
        mkv = MakeMKV(media.path)
        titles_list = get_titles(mkv)
        longest_title_index = find_longest_title(titles_list)
        if not check_auto():
            rip_skip = input("Press enter to convert this title to MKV, or 's' to skip this disc: ")
            while True:
                if rip_skip == "":
                    break
                elif rip_skip.lower() == "s":
                    skip_disc()
                else:
                    print("Invalid input. Please try again.")
        mkv.mkv(longest_title_index, output_dir=folder_path, cache=None, minlength=None)
    except SkipDisc:
        raise


def get_titles(mkv): #get list of titles from disc for makemkv 
    disc_info = mkv.info()
    titles = disc_info['titles']
    return titles


def find_longest_title(titles): #find longest title on disc
    longest_title_index = None
    longest_title_length = 0

    for i, title_info, in enumerate(titles):
        title_length = title_info["length"]
        title_length_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], title_length.split(":")))
        if title_length_seconds > longest_title_length:
            longest_title_index = i
            longest_title_length = title_length_seconds
    print(f"Longest title is {longest_title_index} with length {longest_title_length}")
    return longest_title_index


def rename_file(folder_path, folder_string): #rename mkv file to match folder
    file_list = os.listdir(folder_path)
    for file in file_list:
        if file.endswith(".mkv"):
            os.rename(os.path.join(folder_path, file), os.path.join(folder_path, folder_string + ".mkv"))


def add_to_log(disc_path): #add disc to log file
    with open("makemkv_log.txt", "a") as disc_log:
        disc_log.write(disc_path + "\n")


if __name__ == "__main__":

    lib_path = get_lib_path(lib_path) # get library path
    dest_path = get_dest_path(dest_path) # get destination path
    skip_logged = get_skip_logged() #check if user wants to skip logged discs
    disc_list = find_discs(lib_path) #get list of discs in library
    
    for disc_path in disc_list: #iterate through found discs
        try: #try-except for skip_disc() function
            if skip_logged == True and disc_path in open("makemkv_log.txt").read(): #check if disc is in log
                continue    
            disc_parent = get_disc_parent(disc_path, lib_path) #get disc parent foldername
            disc_info = parse_disc(disc_parent) #parse disc parent foldername for disc info
            media = make_media(disc_info, disc_path) #create media object with parsed info  
            print_found_media(media) #print media info
            results = search_tmdb(media) #search tmdb
            matched, i = find_match(results, media) #check for exact match with media title and year
            if matched == False:
                print_all_results(results) #print all search results
                custom, choice = get_results_choice(results, media) #get user choice from search results
                if custom == False:
                    edit_media_choice(media, choice, results) #edit media info based on user choice
            else:
                edit_media_choice(media, i, results) #edit media info based on exact match
            folder_path, folder_string = makemkv_folder(media, dest_path) #create folder for makemkv output
            mkvgen(media, folder_path) #generate mkv file
            rename_file(folder_path, folder_string) #rename mkv file to match folder
            add_to_log(disc_path) #add disc to log file
        
        except SkipDisc: #skip disc
            continue 
