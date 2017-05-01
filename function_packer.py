def summation(input):
    print "Summation function called."
    print "Raw inpupt: " + str(input)
    # Convert bytearray to string

    data = eval(str(input))

    print "data: " + str(input)

    sum = 0
    for item in data:
        sum += item

    print "Sum: " + str(sum)

def image_histrogram(input):
    print "Histrogrm function"

    # Discard bmp header
    import Image
    import io
    image = Image.open(io.BytesIO(input))
    print "Image size: " + str(image.size)

    # Calculate histogram
    hist = [0] * 255

    for x in range(0, image.size[0]):
        for y in range(0, image.size[1]):
            hist[image.getpixel((x,y))] += 1

    print hist

if __name__ == '__main__':
    import marshal
    marshal.dump(summation.func_code, open('summation_python2_7.p', 'wb'))
    marshal.dump(image_histrogram.func_code, open('histogram_python2_7.p', 'wb'))
