#!/usr/bin/python
import os
import tempfile
import subprocess
import shutil
from gimpfu import *

# 
# velociredactor.py
# 
# Batch redact from similar PDFs in a directory
# 
# Powered by: 
# 	GIMP, 
# 	GhostScript, 
# 	ImageMagick
# 	Python
# 	Bash(?)
#	Deskew Plugin for GIMP
# 
# Basically this works when called from GIMP's Python-Fu:
# pdb.python_fu_velociredactor(<tmpl>, <idir>, <odir>)
# 
# Developed on Ubuntu 12.04.3 LTS 32-bit
# 
# 2013 Evan Rowley
# 
# velociredactor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 



def velociredactor(tmpl, src, dest, ignore=None):
	if os.path.isdir(src):
		if not os.path.isdir(dest):
			os.makedirs(dest)
		files = os.listdir(src)
		if ignore is not None:
			ignored = ignore(src, files)
		else:
 			ignored = set()
		for f in files:
			if f not in ignored:
				velociredactor(tmpl, 
					os.path.join(src, f), 
					os.path.join(dest, f), 
					ignore)
	else:
		# Is src a PDF file ?_?
                fileName, fileExtension = os.path.splitext(src)
		if fileExtension == ".pdf":
			# Turns out, src IS a PDF file! :D
			
			#print fileName
			tup = (fileName, "%d", "png")
			gsPNGcmd = '.'.join(tup)
			#print gsPNGcmd

		
			# Create Temp Directory
			tdir = tempfile.mkdtemp()
			print tdir

			gsPNGcmd = '/'.join([tdir, os.path.basename(gsPNGcmd)])
			gsPNGcmd = bashFriendlyPath(gsPNGcmd)
			#print("gsPNGcmd: %s" % gsPNGcmd)

			tdest = '/'.join([tdir, os.path.basename(src)])
                        tdest = bashFriendlyPath(tdest)
			#print("tdest: %s" % tdest)
			#print("src: %s" % src)
			shutil.copyfile(src, tdest)
			pdf_file_list = sorted(scanDirForPDFs(tdir))
			#print(pdf_file_list)

			sub = ''.join([
			        'gs',
			        ' -q',
			        ' -dNOPAUSE',
			        ' -dBATCH',
			        ' -sDEVICE=pngalpha',
			        ' -r300',
			        ' -dEPSCrop',
			        ' -sOutputFile=',
			        gsPNGcmd,
			        ' ',
			        tdest
			])
			subprocess.check_output([sub], shell=True)

			png_file_list = sorted(scanDirForPNGs(tdir))
			#print(png_file_list)

			## START MODIFY PNG FILES ##

			image = pdb.file_png_load(png_file_list[0], png_file_list[0])
			drawable = image.active_layer
			pdb.gimp_deskew_plugin(image,drawable,0,0,0,0,0,run_mode=0)
			backlayer = pdb.gimp_layer_new(image, image.width, image.height, 0, 'backlayer', 100, 0)
			pdb.gimp_image_add_layer(image, backlayer, 1)
			pdb.gimp_context_set_background((255,255,255))
			pdb.gimp_drawable_fill(backlayer, 1)
			pdb.gimp_image_lower_layer_to_bottom(image, backlayer)
			template = pdb.gimp_file_load_layer(image,tmpl)
			pdb.gimp_image_add_layer(image,template, -1)
			pdb.gimp_image_raise_layer_to_top(image, template)
			image.merge_visible_layers(2)
			pdb.file_png_save(image, image.active_layer, png_file_list[0], png_file_list[0], 0, 9, 1, 1, 1, 1, 1)
			pdb.gimp_image_delete(image)

			## END MODIFY PNG FILES ##

			## START PNGs 2 PDFs ##
			
			# PNGs 2 PDFs via ImageMagick
			for png_file in png_file_list:
			        fileName2, fileExtension2 = os.path.splitext(png_file)
				pdf_file = '.'.join([
			                fileName2,
			                'pdf'
				])
				sub = ' '.join([
					'/usr/bin/convert',
					png_file,
					pdf_file
				])
				pdf_file_list.append(pdf_file)
				print(sub)
				subprocess.check_output([sub], shell=True)

			pdf_file_list = sorted(pdf_file_list)
			#print(pdf_file_list)

			## END PNGs 2 PDFs ##

			## START MULTI PDFs to ONE PDF ##

			# Consolidate PDFs via GhostScript

			fileName, fileExtension = os.path.splitext(tdest)
			redacted_pdf = '.'.join([fileName, "redacted", 'pdf'])
			sub = ''.join([
				''.join([
					'gs',
					' -q',
					' -dNOPAUSE',
					' -dBATCH',
					' -dSAFER',
					' -sDEVICE=pdfwrite',
					' -sOutputFile=',
					redacted_pdf,
					' ',
				]),
				' '.join(
					pdf_file_list
				)
			])
			print(sub)
			subprocess.check_output([sub], shell=True)

			#pdf_file_list = sorted(scanDirForPDFs(tdir))
			#print(pdf_file_list)
			## END MULTI PDFs to ONE PDF ##

			shutil.copyfile(redacted_pdf, dest)

			# Clear Temp Directory
			#print("Cleaning temporary files in %s" % tdir)
			for the_file in os.listdir(tdir):
			        file_path = os.path.join(tdir, the_file)
			        try:
			                os.unlink(file_path)
			                #print("Deleted temporary file %s" % the_file)
			        except Exception, e:
			                print e
			#print("File deletions complete. Removing temporary directory.")
			# Close Temp Directory
			os.removedirs(tdir)
			#print("Deleted %s" % tdir)

	return dest

def scanDirForPDFs(adir):
	scannedPDFs = []
	for dirpath, dirnames, files in os.walk(adir):
		for afile in files:
			# If file is a PDF, add to our list
			fileName, fileExtension = os.path.splitext(afile)
			if fileExtension == ".pdf":
				scannedPDFs.append('/'.join([dirpath,afile]))
	return scannedPDFs

def scanDirForPNGs(adir):
        scannedPNGs = []
        for dirpath, dirnames, files in os.walk(adir):
                for afile in files:
                        # If file is a PNG, add to our list
                        fileName, fileExtension = os.path.splitext(afile)
                        if fileExtension == ".png":
                                scannedPNGs.append('/'.join([dirpath,afile]))
        return scannedPNGs

def bashFriendlyPath(astring):
	astring = astring.replace(" ", "_")
	astring = astring.replace(",","")
	astring = astring.replace("(","")
	astring = astring.replace(")","")
	astring = astring.replace("{","")
	astring = astring.replace("}","")
	astring = astring.replace("[","")
	astring = astring.replace("]","")
	#astring = astring.replace("\"", "\\\" ")
	#astring = astring.replace("\'", "\\\' ")
	astring = astring.replace("$", "")
	astring = astring.replace("#", "")
	astring = astring.replace(";", "")
	astring = astring.replace("~", "")
	astring = astring.replace(">", "")
	astring = astring.replace("<", "")
	astring = astring.replace("|", "")
	return astring


register(
        "python_fu_velociredactor",
        "Perform fancy redactions on many PDFs",
        "Perform fancy redactions on many PDFs",
        "Evan Rowley",
        "Evan Rolwey",
        "2013",
        "<Toolbox>/MyScripts/Velociredactor",
        "*",
        [
                (PF_STRING , "tmpl", "Template XCF", ""),
                (PF_STRING , "src", "Source Folder", ""),
                (PF_STRING , "dest", "Destination Folder", ""),
        ],
        [],
        velociredactor)

main()
