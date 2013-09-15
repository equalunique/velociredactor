#!/usr/bin/python
import os
import tempfile
import argparse
import subprocess
import shutil

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

			#s.redact(png_file_list[0], templ) #Send 
			#while s.redacting()
			#	# wait 3s
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


#What arguments are acceptable
parser = argparse.ArgumentParser(description='Redact info from many PDFs based on GIMP template')
parser.add_argument('--idira', help='Input directory containing PDFs and \/ or other directories', required=True)
parser.add_argument('--odira', help='Output directory to mirror the input directory', required=True)
parser.add_argument('--tmpla', help='GIMP XCF file as template for redaction', required=True)
args = parser.parse_args()

idira = os.path.abspath(args.idira)
odira = os.path.abspath(args.odira)
tmpla = os.path.abspath(args.tmpla)



#scanPDFs = []
#scanPDFs = scanDirForPDFs(idir)
#print scanPDFs
velociredactor(tmpla, idira, odira)
#scanPDFs = scanDirForPDFs(odir)
#print scanPDFs
