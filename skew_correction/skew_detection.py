import os
import imghdr
import optparse

import numpy as np
import matplotlib.pyplot as plt
from skimage import io
from skimage.feature import canny
from skimage.color import rgb2gray
from skimage.transform import hough_line, hough_line_peaks


class SkewDetect:

    # Define the value of pi/4
    piby4 = np.pi / 4

    # Constructor to initialize the class variables
    def __init__(
        self,
        input_file=None,
        batch_path=None,
        output_file=None,
        sigma=3.0,
        display_output=None,
        num_peaks=20,
        plot_hough=None
    ):

        self.sigma = sigma
        self.input_file = input_file
        self.batch_path = batch_path
        self.output_file = output_file
        self.display_output = display_output
        self.num_peaks = num_peaks
        self.plot_hough = plot_hough
    # def __init__(self, image_path, output_image_path, sigma, plot_hough):
    #     # Define the file path
    #     self.image_path = image_path
    #     self.output_image_path = output_image_path
    #     self.sigma = sigma
    #     self.plot_hough = plot_hough

    # Function to write data to a file
    def write_to_file(self, wfile, data):
        for key, value in data.items():
            wfile.write(f"{key}: {value}\n")
        wfile.write("\n")

    # Function to get the maximum frequency element in an array
    def get_max_freq_elem(self, arr):
        freqs = {}
        max_freq = 0
        max_arr = []

        for i in arr:
            freqs[i] = freqs.get(i, 0) + 1
            max_freq = max(max_freq, freqs[i])

        for key, value in freqs.items():
            if value == max_freq:
                max_arr.append(key)

        return max_arr
    
    # Function to display the Hough transform
    def display_hough(self, h, a, d):
        import numpy as np
        import matplotlib.pyplot as plt

        # Apply logarithmic scaling to enhance visualization
        h_log = np.log(1 + h)

        # Define the extent of the image
        extent = [np.rad2deg(a[-1]), np.rad2deg(a[0]), d[-1], d[0]]

        # Display the Hough transform
        plt.imshow(h_log, extent=extent, cmap=plt.cm.gray, aspect=1.0 / 90)
        plt.show()
    
    def compare_sum(self, value):
        if value >= 44 and value <= 46:
            return True
        else:
            return False
        
    def display(self, data):
        print ("Image File: " + data["Image File"])
        print("Results:" + data)
        for i in data:
            print(i + ": " + str(data[i]))


    def calculate_deviation(self, angle):
        angle_in_degrees = np.abs(angle)
        deviation = np.abs(SkewDetect.piby4 - angle_in_degrees)

        return deviation
    

    def run(self):

        if self.display_output:
            if self.display_output.lower() == 'yes':
                self.display_output = True
            else:
                self.display_output = False

        if self.plot_hough:
            if self.plot_hough.lower() == 'yes':
                self.plot_hough = True
            else:
                self.plot_hough = False

        if self.input_file is None:
            if self.batch_path:
                self.batch_process()
            else:
                print("Invalid input, nothing to process.")
        else:
            self.process_single_file()

    def check_path(self, path):

        if os.path.isabs(path):
            full_path = path
        else:
            full_path = os.getcwd() + '/' + str(path)
        return full_path
    

    def process_single_file(self):

        file_path = self.check_path(self.input_file)
        res = self.determine_skew(file_path)

        if self.output_file:
            output_path = self.check_path(self.output_file)
            wfile = open(output_path, 'w')
            self.write_to_file(wfile, res)
            wfile.close()

        return res
    

    def determine_skew(self, img_file):
        from skimage import io, color
        img = io.imread(img_file)
        img_gray = color.rgb2gray(img)

        #plot the grayscale image
        plt.imshow(img_gray, cmap='gray')
        plt.show()


        edges = canny(img_gray, sigma=self.sigma)
        h, a, d = hough_line(edges)
        _, ap, _ = hough_line_peaks(h, a, d, num_peaks=self.num_peaks)

        # plot the hough lines
        plt.imshow(img_gray, cmap='gray')
        for _, angle, dist in zip(*hough_line_peaks(h, a, d, num_peaks=self.num_peaks)):
            y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
            y1 = (dist - img_gray.shape[1] * np.cos(angle)) / np.sin(angle)
            plt.plot((0, img_gray.shape[1]), (y0, y1), '-r')
        plt.xlim((0, img_gray.shape[1]))
        plt.ylim((img_gray.shape[0], 0))
        plt.axis('off')
        plt.tight_layout()
        plt.show()

        #plot the hough peaks on the hough transform
        print("Hough Peaks: ", ap)



        if len(ap) == 0:
            return {"Image File": img_file, "Message": "Bad Quality"}

        absolute_deviations = [self.calculate_deviation(k) for k in ap]
        average_deviation = np.mean(np.rad2deg(absolute_deviations))
        ap_deg = [np.rad2deg(x) for x in ap]

        bin_0_45 = []
        bin_45_90 = []
        bin_0_45n = []
        bin_45_90n = []

        for ang in ap_deg:

            deviation_sum = int(90 - ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_45_90.append(ang)
                continue

            deviation_sum = int(ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_0_45.append(ang)
                continue

            deviation_sum = int(-ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_0_45n.append(ang)
                continue

            deviation_sum = int(90 + ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_45_90n.append(ang)

        angles = [bin_0_45, bin_45_90, bin_0_45n, bin_45_90n]
        lmax = 0

        for j in range(len(angles)):
            l = len(angles[j])
            if l > lmax:
                lmax = l
                maxi = j

        if lmax:
            ans_arr = self.get_max_freq_elem(angles[maxi])
            ans_res = np.mean(ans_arr)

        else:
            ans_arr = self.get_max_freq_elem(ap_deg)
            ans_res = np.mean(ans_arr)

        data = {
            "Image File": img_file,
            "Average Deviation from pi/4": average_deviation,
            "Estimated Angle": ans_res,
            "Angle bins": angles}

        if self.display_output:
            self.display(data)

        if self.plot_hough:
            self.display_hough(h, a, d)
        return data

if __name__ == '__main__':

    parser = optparse.OptionParser()

    parser.add_option(
        '-b', '--batch',
        default=None,
        dest='batch_path',
        help='Path for batch processing')
    parser.add_option(
        '-d', '--display',
        default=None,
        dest='display_output',
        help='Display logs')
    parser.add_option(
        '-i', '--input',
        default=None,
        dest='input_file',
        help='Input file name')
    parser.add_option(
        '-n', '--num',
        default=20,
        dest='num_peaks',
        help='Number of Hough Transform peaks',
        type=int)
    parser.add_option(
        '-o', '--output',
        default=None,
        dest='output_file',
        help='Output file name')
    parser.add_option(
        '-p', '--plot',
        default=None,
        dest='plot_hough',
        help='Plot the Hough Transform')
    parser.add_option(
        '-s', '--sigma',
        default=3.0,
        dest='sigma',
        help='Sigma for Canny Edge Detection',
        type=float)
    options, args = parser.parse_args()
    skew_obj = SkewDetect(
        options.input_file,
        options.batch_path,
        options.output_file,
        options.sigma,
        options.display_output,
        options.num_peaks,
        options.plot_hough)
    skew_obj.run()


    # def detect_skew_angle(rows):
    #     # Initialize array to store skew angles per row
    #     skew_angles = []
        
    #     # Loop through each row
    #     for row in rows:
    #         # Convert row to grayscale
    #         gray_row = np.array([1 if x == 255 else 0 for x in row])
            
    #         # Check if all pixel values are the same
    #         if np.all(gray_row == gray_row[0]):
    #             # If all pixel values are the same, skip this row
    #             continue
            
    #         # Compute the center of mass of the row
    #         x = np.arange(len(row))
    #         x_cog = np.sum(x * gray_row) / np.sum(gray_row)
            
    #         # Compute the skew angle based on the center of mass
    #         skew_angle = np.arctan2(x_cog - len(row) / 2, len(row))
    #         skew_angles.append(skew_angle)
        
    #     return skew_angles

    # def compute_quality(rotated_image):
    #     # Simple quality measure: sum of pixel values
    #     quality = np.sum(rotated_image)
    #     return quality

    # def find_best_skew_angle(image):
    #     # Define range of candidate angles
    #     candidate_angles = np.arange(-10, 11, 1)  # Adjust range as needed
        
    #     # Initialize variables to store best angle and quality
    #     best_angle = 0
    #     best_quality = float('-inf')
        
    #     # Convert image to numpy array
    #     image_array = np.array(image)
        
    #     # Assuming each row contains single characters
    #     rows = image_array.tolist()
        
    #     # Detect skew angles for each row
    #     skew_angles = detect_skew_angle(rows)

    #     # Plot histogram of skew angles
    #     plot_skew_angle_histogram(skew_angles)

        
    #     # Iterate over candidate angles
    #     for angle in candidate_angles:
    #         # Rotate the image
    #         rotated_image = image.rotate(angle, resample=Image.BICUBIC, expand=True)
            
    #         # Compute the quality of the rotated image
    #         quality = compute_quality(rotated_image)
            
    #         # Update best angle and quality if necessary
    #         if quality > best_quality:
    #             best_angle = angle
    #             best_quality = quality
        
    #     return best_angle

    # def rotate_image(image, angle):
    #     # Rotate the image by the specified angle
    #     rotated_image = image.rotate(np.degrees(angle), resample=Image.BICUBIC, expand=True)
    #     return rotated_image

    # def plot_skew_angle_histogram(skew_angles):
    #     # Display the histogram
    #     plt.figure(figsize=(8, 6))
    #     plt.hist(np.degrees(skew_angles), bins=30, color='blue', alpha=0.7)
    #     plt.xlabel('Skew Angle (degrees)')
    #     plt.ylabel('Frequency')
    #     plt.title('Histogram of Skew Angles')
    #     plt.grid(True)
    #     plt.show()



# Example usage
# Read image
# image_path = './assets/image-rotated.jpg'
# image = Image.open(image_path).convert('L')  # Convert to grayscale

# # Find the best skew angle
# best_angle = find_best_skew_angle(image)
# print("Best skew angle:", best_angle)

# # Rotate the image with the best angle
# rotated_image = image.rotate(best_angle, resample=Image.BICUBIC, expand=True)

# # Show the original and rotated images
# plt.figure(figsize=(10, 5))
# plt.subplot(1, 2, 1)
# plt.imshow(image, cmap='gray')
# plt.title('Original Image')
# plt.axis('off')

# plt.subplot(1, 2, 2)
# plt.imshow(rotated_image, cmap='gray')
# plt.title('Corrected Image')
# plt.axis('off')

# plt.show()