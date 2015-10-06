#!/usr/bin/env python
"""
Take a screenshot of a Twitter profile.
Removes some clutter and crops before saving.

Requirements:
 * Python 2 (tested on 2.7)
 * pip install pillow selenium
 * ChromeDriver https://code.google.com/p/selenium/wiki/ChromeDriver
"""
from __future__ import print_function, unicode_literals
import argparse
from PIL import Image  # pip install pillow
from selenium import webdriver  # pip install selenium
import StringIO
import time


def get_url(url_or_username):
    """
    Given https://twitter.com/gutendelight, @gutendelight or gutendelight,
    return https://twitter.com/gutendelight
    """
    if url_or_username.startswith("http"):
        return url
    else:
        return "https://twitter.com/" + url_or_username.lstrip("@")


def username_from_url(url):
    """ Given https://twitter.com/gutendelight, return gutendelight """
    pos = url.rfind("/")
    return url[pos+1:]


def delete_element_by_class_name(class_name):
    """ Delete an element from the page """

    element = driver.find_element_by_class_name(class_name)
    driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element)


def take_shot(url):
    """
    Load the page, remove some clutter and
    return a screenshot as a Pillow image
    """

    # Load the webpage
    driver.get(url)

    # Remove some clutter
    delete_element_by_class_name('BannersContainer')
    delete_element_by_class_name('topbar')
    delete_element_by_class_name('SignupCallOut')
    delete_element_by_class_name('trends')
    delete_element_by_class_name('user-actions-follow-button')

    # Bit of extra time to let it finish loading/removing
    time.sleep(0.5)

    # Save the image immediately to disk
    # driver.save_screenshot(outfile)

    # Get the image as binary data without saving to disk (yet)
    # and return it as a Pillow image
    png = driver.get_screenshot_as_png()
    im = Image.open(StringIO.StringIO(png))
    return im


def crop_image(im):
    """ Crop and return the image """
    # Crop:
    #  * 90px from top for header and down to just above profile image
    #  * 20px from right for scrollbars
    left = 0
    top = 90
    right = im.width - 20
    bottom = im.height

    # Now centre in 900px
    width = right - left
    if width > 900:
        gap = (width - 900)/2
        left += gap
        right -= gap

    im = im.crop((left, top, right, bottom))
    return im


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Take a screenshot of a Twitter profile.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('url', help="Username or URL to screenshot")
    parser.add_argument('-o', '--outfile', help="Output filename")
    args = parser.parse_args()

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()
    driver.set_window_size(1000, 800)

    url = get_url(args.url)
    im = take_shot(url)
    im = crop_image(im)

    if not args.outfile:
        args.outfile = username_from_url(url) + ".png"
    im.save(args.outfile)

    driver.quit()

# End of file
