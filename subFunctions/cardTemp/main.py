from bs4 import BeautifulSoup
import textwrap
import subprocess
import os
from dotenv import load_dotenv


def wrapText(txtElm, newTxt, soup, maxChars=30, lineHeight=2.0):
    """
    Wraps long text into multiple liines using SVG tspan elements.

    Args:
        txtElm: BeautifulSoup text element to modify
        newTxt (str): New text content to wrap and insert
        soup: BeautifulSoup object for creating new tspan elements
        maxChars (float): Maximum characters per line before wrapping (default: 39.5)
        lineHeight (float): Line spacing multiplier relative to font size (default: 2.0)

    Returns:
        None: Modifies the txtElm in place
    """

    # Get original position and font size
    x = txtElm.get('x', '0')
    y = txtElm.get('y', '0')
    fontSize = txtElm.get('font-size', '12')

    # Extract numeric font size for line spacing calculation
    try:
        fontSizeNum = float(fontSize.replace('px', '').replace('pt', ''))
    except:
        fontSizeNum = 12

    lineSpacing = fontSizeNum * lineHeight

    # Clear existing content
    txtElm.clear()

    # Wrap text into lines
    lines = textwrap.wrap(newTxt, width=maxChars)

    for i, line in enumerate(lines):
        tspan = soup.new_tag('tspan')
        tspan.string = line
        tspan['x'] = x

        if i == 0:
            # First line uses origin y position
            tspan['y'] = y
        else:
            # Subsequent lines offset by line spacing
            try:
                yNum = float(y)
                tspan['y'] = str(yNum+(i*lineSpacing))
            except:
                tspan['dy'] = str(lineSpacing)

        txtElm.append(tspan)


def getSVGdims(svgCon):
    soup = BeautifulSoup(svgCon, 'xml')
    svgElm = soup.find('svg')

    if not svgElm:
        print("WARNING: No SVG element found, using default 1920x1080")
        return 1920, 1080

    print("SCG attributes:", dict(svgElm.attrs))

    width = svgElm.get('width')
    height = svgElm.get('height')
    viewBox = svgElm.get('viewBox')
    print(f"Width: {width}\nHeight: {height}\nViewBox: {viewBox}")

    if viewBox:
        parts = viewBox.split()
        if len(parts) >= 4:
            width = int(float(parts[2]))
            height = int(float(parts[3]))
            return width, height

    def cleanMeasure(txt):
        return int(float(txt.replace('px', '').replace('pt', '')))

    if width and height:
        width = cleanMeasure(width)
        height = cleanMeasure(height)
        return width, height

    return 1920, 1080


def svgToPng(svgCon, svgFile, pngFile, width=None, height=None, quality=95):
    # Get SVG dimensions if not provided
    if width is None or height is None:
        svgWidth, svgHeight = getSVGdims(svgCon)
        width = width or svgWidth
        height = height or svgHeight

    load_dotenv()
    ink = os.getenv('ink')
    cmd = [ink, '--export-filename', pngFile]
    if width and height:
        cmd.extend(['--export-width', str(width),
                   '--export-height', str(height)])

    cmd.append(svgFile)
    # print(f"cmd line:\n{cmd}")

    subprocess.run(cmd)
    print(f"✓ Converted: {pngFile}")


def replaceSVGtxt(svgFileIn: str, topTxt: str, botTxt: str, svgFile='modifiedImg.svg', maxChar=30, lineHeight=2.0):
    """
    Replaces text in an SVG file with new text that automatically wraps to multiple lines.

    Args:
        svgFileIn (str): Path to the input SVG file
        topTxt (str): New text for the top text element (will be wrapped if too long)
        botTxt (str): New text for the bottom text element (will be wrapped if too long)
        saveFile (str): Path for the output SVG file (default: 'modifiedImg.svg')

    Returns:
        None: Creates a new SVG file with replaced text
    """

    # Load SVG
    with open(svgFileIn, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'xml')

    # Find all text elements
    txtElms = soup.find_all(['text', 'tspan'])
    txtElms = [elm for elm in txtElms if elm.get_text(strip=True)]

    # print(f"Found {len(txtElms)} text elements")

    # Show all text elements for debugging
    # for i, elm in enumerate(txtElms):
    #     print(f"Element {i}: '{elm.get_text(strip=True)}'")

    # Replace first two text elements
    if len(txtElms) >= 1:
        oldTop = txtElms[0].get_text(strip=True)
        wrapText(txtElms[0], topTxt, soup, maxChar, lineHeight)
        # print(f"Replace Top Text:\n{oldTop}\nwith\n{topTxt}")

    if len(txtElms) >= 2:
        oldBot = txtElms[2].get_text(strip=True)
        wrapText(txtElms[2], botTxt, soup, maxChar, lineHeight)
        # print(f"Replace Bottom Text:\n{oldBot}\nwith\n{botTxt}")

    # Save modified SVG
    with open(svgFile, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    # print(f"✓ Saved: {svgFile}")

    baseName = svgFile.replace('.svg', '.png')
    svgCon = str(soup)
    pngFile = baseName
    svgToPng(svgCon, svgFile, pngFile)


if __name__ == '__main__':
    """
    Main execution block - replaces text in 'img.svg' with new content.

    The script will:
    1. Load 'img.svg'
    2. Find text elements
    3. Replace first element with topTxt (wrapped if needed)
    4. Replace third element with botTxt (wrapped if needed)
    5. Save result as 'modifiedImg.svg'
    """

    replaceSVGtxt(
        svgFileIn='img.svg',
        topTxt='>--Top Line of Text, with a considerable amount of text, since it will hold a whole ______',
        botTxt='>--Bottom Line of Text, with slightly less text, for it is oneliner',
        svgFile='modifiedImg.svg'
    )
