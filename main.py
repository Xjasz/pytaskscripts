import argparse
import json
from projects.btc.keygen import run_keygen
from projects.btc.passgen import run_passgen
from projects.crypto.monitor import run_monitor
from projects.stake.stake_shared import run_stake_game
from utils.logger import get_logger

with open("config.json") as f:
    config = json.load(f)

def dispatch(task, log_mode):
    logger = get_logger(task, log_mode)
    logger.info(f"Running Task: {task} | Log Mode: {log_mode}")
    
    if task == "stake_task":
        mode = config["stake_task"]["mode"]
        if mode in ("CRASH", "SLIDE"):
            run_stake_game(mode=mode, log=logger)
        elif mode == "BOTH":
            run_stake_game(mode="CRASH", log=logger)
            run_stake_game(mode="SLIDE", log=logger)
    elif task == "btc_task":
        mode = config["btc_task"]["mode"]
        if mode == "KEY":
            process_amount = config["btc_task"]["process_amount"]
            run_keygen(process_amount=process_amount, log=logger)
        elif mode == "PASS":
            pass_type = config["btc_task"]["pass_type"]
            process_amount = config["btc_task"]["process_amount"]
            run_passgen(pass_type=pass_type, process_amount=process_amount, log=logger)
    elif task == "crypto_monitor":
        mode = config["crypto_monitor"]["mode"]
        run_monitor(mode=mode, log=logger)
    else:
        logger.error(f"Invalid task: {task}")
        print("Unknown task.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pytaskscripts runner")
    parser.add_argument("task", help="Task to run")
    parser.add_argument("--log_mode", help="Log file mode", choices=["append", "write"], default="append")
    args = parser.parse_args()
    dispatch(args.task, args.log_mode)