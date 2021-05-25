import sys
import torch
from utils import *



def run():
    while True:
        cmd = input("\nViDB> ")

        if cmd == "exit":
            sys.exit("The program is terminated.\n")
        else:
            cmd = cmd.split()
            if cmd[0] == "browse":
                # [Usage] browse <k> <random/cluster>
                browse(FEAT_DIR, int(cmd[1]), cmd[2])
            elif cmd[0] == "query":
                # [Usage] query <target_idx> <k> <nearest/farthest> <content/style>
                nearest = (cmd[3] == "nearest")
                find_instance(FEAT_DIR, int(cmd[1]), int(cmd[2]), nearest, cmd[4], device)
            elif cmd[0] == "query-tag":
                # [Usage] query-tag <target_idx> <k> <all/partial> <tags>
                tags = cmd[4].split(",")
                find_instance_by_tag(FEAT_DIR, int(cmd[1]), int(cmd[2]), cmd[3], tags, device)
            elif cmd[0] == "query-range":
                # [Usage] query-range <group_idx> <k> <content/style>
                group_idx = cmd[1].split(",")
                group_idx = [int(idx) for idx in group_idx]
                find_instance_by_range(FEAT_DIR, group_idx, int(cmd[2]), cmd[3], device)


if __name__ == "__main__":
    IMG_DIR = "./data/database/image"
    FEAT_DIR = "./data/database/feature"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # extract_feature(IMG_DIR, FEAT_DIR, device)
    run()
