from datetime import datetime
from ppadb.client_async import ClientAsync as AdbClient
from PIL import Image
import asyncio
import aiofiles
import cv2
import numpy
import os
import time
import webp
import config


class Bot():
    # for screen 1080x2280
    COORDS = {
        "VIEW_PROFILE": (70, 60),
        "CLOSE_PROFIL": (1860, 100),
        "VIEW_HOME": (90, 990),
    }

    width = None
    height = None

    def __init__(self, device) -> None:
        self.device = device
        self.name = self.device.serial
        self.manager = TaskManager(self)

    def _resource_path_for(self, filename: str) -> str:
        return os.path.abspath(f"./resources/{filename}")

    def _has_image(self, screen, target):
        # https://bits.mdminhazulhaque.io/opencv/find-image-in-another-image-using-opencv-and-numpy.html
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = numpy.where(res >= threshold)
        try:
            assert loc[0][0] > 0
            assert loc[1][0] > 0
            return (loc[1][0], loc[0][0])
        except:
            return (-1, -1)

    def screenshot_name(self, name_date = False, file_extension=".jpeg"):
        if name_date is False:
            filename = f"{self.name}{file_extension}"
        else:
            current_datetime = datetime.now()
            str_current_datetime = str(current_datetime)
            filename = f"{str_current_datetime}{file_extension}"
        filepath = os.path.abspath(f"./screenshots/{filename}")
        return filepath

    async def current_screenshot(self, file_extension=".jpeg"):
        await self.manager.capture()
        return self.screenshot_name(file_extension=file_extension)

    async def show_profile(self):
        await self.manager.tap(self.COORDS["VIEW_PROFILE"])

    async def show_city(self):
        pass

    async def show_map(self):
        pass

    async def work(self):
        if self.width is None:
            await self.manager.find_resolution()

        await self.manager.capture()
        time.sleep(0.5)


class TaskManager():

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.device = self.bot.device

    def _convert_img_to_webp(self, file_to_convert) -> str:
        if os.path.exists(file_to_convert) is False:
            return
        filename, _ = os.path.splitext(file_to_convert)
        img = Image.open(file_to_convert)
        filepath = os.path.abspath(f"{filename}.webp")
        webp.save_image(img, filepath, quality=70)
        return filepath

    async def capture(self, name_date = False, convert_to_webp = False) -> str:
        result = await self.device.screencap()
        filepath = self.bot.screenshot_name(name_date=name_date)
        async with aiofiles.open(f"{filepath}", mode="wb") as f:
            await f.write(result)
        if convert_to_webp is True:
            filepath = self._convert_img_to_webp(filepath)
        print(f"[{self.bot.name}]:TaskManager:capture: {filepath}")
        return filepath

    async def find_resolution(self):
        # this return something like Physical size: 1080x2280
        # so, we neeed to parse it to retrieve (1080,2280)
        wm_size = await self.device.shell("wm size")
        size = wm_size[wm_size.find(":")+2:].split("x")
        self.bot.width, self.bot.height = list(map(lambda s: int(s), size))
        wxh = f"{self.bot.width}x{self.bot.height}"
        print(f"[{self.bot.name}]:TaskManager:find_resolution: {wxh}")

    async def tap(self, coord):
        x, y = coord
        cmd = f"input tap {x} {y}"
        await self.device.shell(cmd)


async def main():
    title = f"=== Rise Of Kingdom - {config.NAME} BOT - {config.VERSION} ==="
    print(title)

    client = AdbClient(**config.ADB_SERVER)
    devices = await client.devices()
    bots = [Bot(device) for device in devices if device]

    await asyncio.gather(*[cheater.work() for cheater in bots])


asyncio.run(main())
