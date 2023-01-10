import tkinter as tk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from tkinter import ttk	
import time
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
from PIL.ExifTags import TAGS
import sys


class Greeting:
	'''Creates the starting TK-window with file-chooser opening'''
	
	@classmethod
	def start(cls):
		'''Initializes the GREATING window toolkit with the image CHOOSER, returns the file path'''
		root = tk.Tk()
		root.title('ECG-helper')
		root_width = 700
		root_height = 500
		root.geometry(f'{root_width}x{root_height}+400+150')
		bg = tk.PhotoImage(file = "bg.png")
		canvas1 = tk.Canvas(root, width=root_width, height=root_height)
		canvas1.pack(fill = "both", expand = True)
		canvas1.create_image(0, 0, image = bg, anchor = "nw")
		canvas1.create_text(root_width/2, root_height/3, text = "Welcome! \nTo get started, select the file with the required ECG:", justify=tk.CENTER, font="Verdana 24", fill='#B63340')
		
	
		def select_image():
			'''Determines the function of open-button: open a file chooser dialog and allow the user to select an image'''
			global filepath
			filetypes = (('image files', '.png'), ('image files', '.jpg'))
			filepath = fd.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
			
			if len(filepath) > 0:
				'''ensure a file path was selected'''
				showinfo(title='The file has been selected!', message='Now select a section of \nthe ECG-line for each lead \n(from the top left point \nto the bottom right point)', parent=root)
				root.destroy()
			else:
				showinfo(title='The file was not selected!', message='Try once more')
					
		open_button = tk.Button(root, activebackground='pink', activeforeground='black', bd='0', fg='#B63340', highlightbackground='#3E4149', relief='flat', overrelief='sunken', text='Select an ECG-image', font="Verdana 17", padx="10", pady="10", command=select_image)
		button_canvas = canvas1.create_window(root_width/3, root_height*2/3, window = open_button)
		root.mainloop()
		return filepath	
	

class Lead:
	'''Opens the image from file and allows to crop all 12 leads from full ECG; save leads as separate files for further usage witth appropriate names'''
	def __init__(self, name, ecg_file):
		self.name = name
		self.cropping = False
		self.x_start, self.y_start, self.x_end, self.y_end = 0, 0, 0, 0
		image = cv2.imread(ecg_file)
		oriImage = image.copy()
		self.mm = self.pixel_in_mm(ecg_file)
		
		def mouse_crop(event, x, y, flags, param):
			'''if the left mouse button was DOWN, start RECORDING (x, y) coordinates and indicate that cropping is being:'''
			if event == cv2.EVENT_LBUTTONDOWN:
				self.x_start, self.y_start, self.x_end, self.y_end = x, y, x, y
				self.cropping = True
				'''Mouse is Moving:'''
			elif event == cv2.EVENT_MOUSEMOVE:
				if self.cropping == True:
					self.x_end, self.y_end = x, y
					'''if the left mouse button was released:'''
			elif event == cv2.EVENT_LBUTTONUP:
				'''record the ending (x, y) coordinates:'''
				self.x_end, self.y_end = x, y
				'''cropping is finished:'''
				self.cropping = False 
				self.box = [self.x_start, self.y_start, self.x_end, self.y_end]
			
				if len(self.box) == 4: 
					'''when two points were found'''
					roi = oriImage[self.box[1]:self.box[3], self.box[0]:self.box[2]]
					cv2.namedWindow(f"{self.name} lead (press 'Enter' to continue)")
					cv2.moveWindow(f"{self.name} lead (press 'Enter' to continue)", self.x_start//2, self.y_start//2)
					cv2.imshow(f"{self.name} lead (press 'Enter' to continue)", roi)
					cv2.imwrite(f"temp_pics/{self.name}.png", roi)
		cv2.namedWindow(f"Select region of {self.name} lead upper-left point >> lower-right point")
		cv2.setMouseCallback(f"Select region of {self.name} lead upper-left point >> lower-right point", mouse_crop)
		
		i = image.copy()
		if not self.cropping:
			cv2.imshow(f"Select region of {self.name} lead upper-left point >> lower-right point", image)
		elif self.cropping:
			cv2.rectangle(i, (self.x_start, self.y_start), (self.x_end, self.y_end), (255, 0, 0), 2)
			cv2.imshow(f"Select region of {self.name} lead upper-left point >> lower-right point", i)
		cv2.waitKey(0)
	
	def pixel_in_mm(self, image):
		'''Finds the resolution of image in meta-data PPI to convert it in mm'''
		with Image.open(image) as img:
			img.load()
		exifdata = img.getexif()
		return round(exifdata[282]/2.54/10)


class ChangeLead:
	'''Transforms each lead-image to binary image'''
	def __init__(self, pic):
		self.pic = pic
	
	@staticmethod
	def cleaning(pic, start_pix):
		'''Static tool for cleaning the image from separate background black points'''
		draw = ImageDraw.Draw(pic)
		width = pic.size[0]  
		height = pic.size[1]
		pix = pic.load()
		
		for x in range(start_pix, width-1, 3):
			for y in range(start_pix, height-1, 3):
				a = pix[x, y]
				sur_colors = []
				sur = [[x-1, y-1], [x, y-1], [x+1, y-1], [x+1, y], 
					   [x+1, y+1], [x, y+1], [x-1, y+1], [x-1, y]]
				for s in sur:
					sur_colors.append(pix[s[0],s[1]])
				w = sur_colors.count(255)
				b = sur_colors.count(0)
	
				if a == 255:
					if w > 5:
						for s in sur:
							draw.point([s[0], s[1]], 255)
					elif w < 2:
						for s in sur:
							draw.point([x, y], 0)
				elif a == 0:
					if b > 7:
						for s in sur:
							draw.point([s[0], s[1]], 0)
					elif b < 2:
						for s in sur:
							draw.point([x, y], 255)		
		del draw
		return pic
	
	def change(self):
		'''Few steps of image-transforming with different tools'''
		with Image.open(self.pic) as img:
			img.load()
		enh = ImageEnhance.Contrast(img)
		out = enh.enhance(3.0)
		fn = lambda x : 255 if x > 40 else 0
		im = out.convert('L').point(fn, mode='1')
		cln = ChangeLead.cleaning(im, 1)
		cln = ChangeLead.cleaning(cln, 2)
		cln = ChangeLead.cleaning(cln, 1)
		cln = ChangeLead.cleaning(cln, 3)
		return cln		


class Isoline:
	'''Finds the starting isoline (first 10 mm of lead-image)'''
	def __init__(self, pic):
		'''Collects parameters of lead-image for usage by this in further classes'''
		self.pic = ChangeLead(pic).change()
		self.width = self.pic.size[0]  
		self.height = self.pic.size[1]
		self.pix = self.pic.load()
		self.isoline_y = self.find_y()
		self.isoline_x = self.find_x()
	
	def find_y(self):
		'''Finds the most intensive 1 mm of y from first 10 mm'''
		iso_y = 0
		blacks = 0
		for y in range(self.height-6):    
			count_blacks = 0
			for x1 in range(60):
				for y1 in range(y, y+6):
					if self.pix[x1, y1] == 0:
						count_blacks += 1
			if count_blacks >= blacks:
				blacks = count_blacks
				iso_y = y
		return iso_y
	
	def find_x(self):
		'''Finds the most intensive 2,5 mm of x from first 10 mm'''
		iso_x = 0
		intens = 0
		for x in range(60):    
			count_blacks = 0
			for x1 in range(x, x+15):
				for y1 in range(self.isoline_y, self.isoline_y+6):
					if self.pix[x1, y1] == 0:
						count_blacks += 1
			if count_blacks >= intens:
				intens = count_blacks
				iso_x = x
		return iso_x


class ECGline(Isoline):
	'''Collects coordinates of ECG-line only avoding the background points'''
	ecg_coord = []
	def __init__(self, pic):
		super().__init__(pic)
	
	def x_last(self):
		if len(ECGline.ecg_coord) > 0:
			return max(ECGline.ecg_coord,key=lambda item:item[0])[0]
		else:
			return 0
	
	def find_start(self, start, span):
		'''Finds start for recursive collection of coordinates'''
		for x in range(start, self.width):
			for y in range(self.isoline_y-span, self.isoline_y+span):
				if y in range(self.height):
					if self.pix[x, y] == 0:
						ECGline.ecg_coord.append((x, y))
						return x, y
				else:
					continue
	
	def registration(self, x, y):
		'''Collecting coordinates connected with main ECG-line'''
		
		sur = [(x-1, y-1), (x, y-1), (x+1, y-1), (x+1, y),       
			   (x+1, y+1), (x, y+1), (x-1, y+1), (x-1, y)]
		for s in sur:
			if s[0] <= 0 or s[0] >= self.width-1 or s[1] <= 0 or s[1] >= self.height-1:
				continue
			elif s in ECGline.ecg_coord:
				continue
			elif self.pix[s[0],s[1]] == 255:
				continue
			elif self.pix[s[0]-1,s[1]] == 255 and self.pix[s[0]+1,s[1]] == 255:
				continue
			else:
				ECGline.ecg_coord.append(s)
				self.registration(s[0],s[1])
		
		while self.width - self.x_last() > 15:
			x, y = self.find_start(self.x_last()+1, 24)
			self.registration(x, y)

		
class RealLead(ECGline):
	'''Redraws the lead-image so that to save only ECG-line'''
	def __init__(self, pic):
		super().__init__(pic)
		self.image = self.draw_ecg()
	
	def draw_ecg(self):
		'''Fills the noising bg-points with white color'''
		draw = ImageDraw.Draw(self.pic)
		for x in range(self.width):
			for y in range(self.height):
				if (x, y) not in ECGline.ecg_coord:
					draw.point([x, y], 255)
		del draw
		return self.pic
        
	def fill_gaps(self):
		'''NOT COMPLETED Fills of line gaps with averages'''
		blacks = {}
		for x in range(24, self.width-24):
			blacks[x] = []
			for y in range(self.isoline_y):
				if self.pix[x, y] == 0:
					blacks[x].append(y)
		

class Cycle(RealLead):
	'''One cardiac cycle from lead with its characteristics'''
	def __init__(self, pic):
		super().__init__(pic)
		self.r = self.wave_R()
		self.j = self.point_J()
		self.local_iso = self.local_iso()
		self.st = self.st_level()		
	
	def mean_line(self, x):
		'''Finds an average y position for specified x of line'''
		blacks = []
		if x in range(self.width):
			for y in range(self.height):
				if self.pix[x, y] == 0:
					blacks.append(y)
		else:
			pass
		if len(blacks) > 0:
			return int(sum(blacks)/len(blacks))
		else:
			return self.isoline_y
			
	def wave_R(self):
		'''R-wave peak of the current QRS complex'''
		for y in range(self.isoline_y):
			for x in range(20, self.width-20):
				if self.pix[x, y] == 0:
					return x, y

	def point_J(self):
		'''Coordinates of J-point for the current Cycle'''
		x = self.r[0] + 15
		y = self.mean_line(x)
		return x, y
			
	def local_iso(self):
		'''Isoline y-coordinate just before the current QRS complex'''
		ys = []
		for x in range(self.r[0]-27, self.r[0]-12):
			ys.append(self.mean_line(x))
		return int(sum(ys)/len(ys))
	
	def st_level(self):
		'''The level of ST-elevetion of the current Cycle'''
		return self.local_iso - self.j[1]
		
													
class Pathology:
	'''Some diseases ECG-criteria'''
	mi = []
	def __init__(self, st_elevation):
		self.st_elevation = st_elevation
	
	def infarction(self):
		'''Defines the location of MI by the names of leads with pathology'''
		if 'III' in self.st_elevation and 'aVF' in self.st_elevation:
			Pathology.mi.append('ECG-signs of the acute inferior (posterior) miocardial infarction')
		elif 'I' in self.st_elevation and 'aVL' in self.st_elevation:
			Pathology.mi.append('ECG-signs of the acute anterior miocardial infarction')
		elif 'V1' in self.st_elevation and 'V2' in self.st_elevation:
			Pathology.mi.append('ECG-signs of the acute septal or right ventricular miocardial infarction')
		elif 'V3' in self.st_elevation and 'V4' in self.st_elevation:
			Pathology.mi.append('ECG-signs of the acute anterior miocardial infarction')
		elif 'V5' in self.st_elevation and 'V6' in self.st_elevation:
			Pathology.mi.append('ECG-signs of the acute lateral miocardial infarction')


class Processing:
	'''Creates the TK-window with Progressbar and provides leads processing'''
	
	lead_names = ('I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')
	ecg_file = Greeting.start()
	for l in lead_names:
		Lead(l, ecg_file)
	cv2.destroyAllWindows()
	
	all_pics = [f'temp_pics/{l}.png' for l in lead_names]
	st_elevation = []
	
	def justwait(self):
		'''TK-window for processing'''
		
		def iter_progress(progress=12):
			'''Increments the progress-line with every lead done'''
					
			root.update_idletasks()
			pb['value'] = 12-progress
			
			if progress == 0:  
				lbl['text'] = 'Done!'
				root.after(1000, root.destroy)
				return
			else:
				lbl['text'] = f'Image processing started.. \n{progress-1}'
			
			p = Processing.all_pics[12-progress]
			i = Isoline(p)
			e = ECGline(p)
			#e.pic.show()
			sys.setrecursionlimit(10000)
			e.registration(e.find_start(0, 12)[0], e.find_start(0, 12)[1])
			re = RealLead(p)
			#re.image.show()
			c1 = Cycle(p)
			print(f'\nFor lead {p.split("/")[1].split(".")[0]}:')
			print('wave R - ', c1.r)
			print('point J - ', c1.j)
			print('isoline - ', c1.local_iso)
			print('level st - ', c1.st)
			
			if p.split("/")[1] == 'V2.png' or p.split("/")[1] == 'V3.png':
				if c1.st > 12:
					Processing.st_elevation.append(p.split("/")[1].split('.')[0])
			else:
				if c1.st > 6:
					Processing.st_elevation.append(p.split("/")[1].split('.')[0])
			ECGline.ecg_coord.clear()
			root.after(1, lambda: iter_progress(progress-1))
			
		root = tk.Tk()
		root.geometry(f'700x500+400+150')
		root.title('Processing...')
		
		pb = ttk.Progressbar(
			root,
			orient='horizontal',
			mode='determinate',
			length=400, 
			maximum=12
		)
		lbl = tk.Label(root, text = f'Image processing started.. \n12', font="Verdana 24")
		lbl.place(relx=0.5, rely=0.3, anchor='center')
		pb.place(relx=0.5, rely=0.5, anchor='center')
		root.after(200, iter_progress)
		root.mainloop()
		
		print(f'\nST-segment is elevated in {", ".join(Processing.st_elevation)}')
		pat = Pathology(Processing.st_elevation)
		pat.infarction()
		result = Conclusion()
		result.finish()


class Conclusion:
	'''Creates the final TK-window with the conclusion'''

	def finish(self):
		'''Creates the final TK-window with the conclusion'''
		root = tk.Tk()
		root.title('ECG-helper')
		root_width = 700
		root_height = 500
		root.geometry(f'{root_width}x{root_height}+400+150')
		bg = tk.PhotoImage(file = "bg.png")
		canvas1 = tk.Canvas(root, width=root_width, height=root_height)
		canvas1.pack(fill = "both", expand = True)
		canvas1.create_image(0, 0, image = bg, anchor = "nw")
		
		# take the data
		damage = ";\n    ".join(Pathology.mi)
		summary = f'Rhythm pacemaker: sinus rhythm \nRegularuty of rhythm: regular \nHeart rate: 72 \nElectrical heart axis: left axis deviation \nArrhythmias: - \nConduction disturbances: - \nHypertrophy: -\nMyocardial damage: \n    {damage}'
			 
		canvas1.create_text(root_width/2, root_height/4, text = summary, justify=tk.LEFT, font="Verdana 15", fill='#B63340')
		root.mainloop()
	

if __name__ == '__main__':
	proc = Processing()
	proc.justwait()
