package gdc_download_and_parse;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.FilenameFilter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.util.ArrayList;

import java.util.zip.ZipEntry;
import java.util.zip.GZIPInputStream;

public class CUtilFileHandling {
	/**
	 * File Handling
	 * 
	 * <P> This class handles listing files and folders.
	 * 
	 * <P> It accepts a folder-name, a file-like search, and an action
	 * 
	 * <P> If the file-like search is left empty ("") then no filtering occurs, else filtering works by finding files which contain the given file-like search value
	 * 
	 * <P> the action is an integer value (0 = search everything, 1 = files only, 2 = folders only) 
	 * 
	 *  @author David Schneider
	 *  @version 1.0
	 *  
	 */
	public ArrayList<String>listFilesAndOrFolders(String folderName, String fileNameLike, int action, Boolean endsWith){
		File folder = new File(folderName);
		File[] files;
		ArrayList<String> list= new ArrayList<String>();
		
		// if action==0 then everything, =1 then files only, =2 then folders only
		
		if (fileNameLike==""){files =folder.listFiles();}
		else { 
			files= folder.listFiles(new FilenameFilter() {public boolean accept(File dir, String name){
				return endsWith?name.endsWith(fileNameLike): name.contains(fileNameLike); } });}
		for(File curfile: files){
			if (action==0 || (action==1 && curfile.isFile()) 
					|| (action==2 && curfile.isDirectory())) {list.add(curfile.getName());}
		}
		return list;
	}
	public CBufferedReaderFile findAndOpenFileForRead2(String filename, String basepath, Boolean close){

		CBufferedReaderFile rtn = null;
		File fin = new File(filename);
		// get the filename in the folder or the filename 
		String filenameToConsider = "",
				origFilenameToConsider = "";
		if (fin.exists()){ 
			if (fin.isDirectory()){
				// we either have a .gz file that we need to unzip OR we have a .txt/.tsv file that is here and/or was already unzipped
				// test for any .gz files
				String fn = "";
				ArrayList<String> fl =listFilesAndOrFolders(filename,".gz",1,true);
				if (fl.size()>0) {fn = fl.get(0);}
				if (fn!="") {// we have a file to unzip
					fn = filename+"/"+fn;
					this._unzipFile(fn, fn+".txt");
					File fr = new File(fn);
					fr.renameTo(new File(fn+".done"));
					filenameToConsider = fn+".txt";
				}
				else { // no file to unzip, so get .txt/.tsv
					fl = listFilesAndOrFolders(filename,".txt",1,true);
					if (fl.size()>0){fn = fl.get(0);}
					if (fn!=""){ filenameToConsider = filename+"/"+fn; }
				}
			}
			else { filenameToConsider = filename; }
			origFilenameToConsider = filenameToConsider.substring(filenameToConsider.lastIndexOf("/")+1);
			try  {
				InputStream fis = new FileInputStream(filenameToConsider); 
				BufferedReader buffread =  new BufferedReader(new InputStreamReader(fis));
				rtn = new CBufferedReaderFile(buffread,origFilenameToConsider);
	    	}
	    	catch(IOException e){e.printStackTrace();}
		}
		return rtn;		
	}

	
	public String readLineFromBufferedReader(BufferedReader buffread, Boolean close){
		String rtn = ""; 
		try {
			if (close){ buffread.close();}
			else {
				if (buffread.ready()) {rtn = buffread.readLine();}
				else {buffread.close(); rtn= null;}
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return rtn;
	}
	public BufferedWriter openFileForWrite(String filename, Boolean truncate, Boolean close){
		OutputStream fos;
		BufferedWriter buffwrite = null;
		try {
			if (truncate){
				File fout = new File(filename);	
				FileWriter filewrite = new FileWriter(fout,false);
				}
			fos = new FileOutputStream(filename);
			buffwrite = new BufferedWriter(new OutputStreamWriter(fos));
		} catch (FileNotFoundException e) { e.printStackTrace();} 
		catch (IOException e) { e.printStackTrace(); }
		return buffwrite;
	}
	public void writeLineToBufferedWriter(BufferedWriter buffwrite, String data, Boolean close){
		try {
			if (close){ buffwrite.close();}
			else {
				buffwrite.write(data+"\n");
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	
    private int _unzipFile(String filename, String outputFilename) {
    	int rtn= 0;
	    File fin = new File(filename);
	    // if file exists and is not a directory then return text of file
	    if(fin.exists() && !fin.isDirectory()){
	    	try ( GZIPInputStream zis = new GZIPInputStream(new FileInputStream(filename))) {
	    		FileOutputStream fos = new FileOutputStream(outputFilename);
	    		int oneByte;
	    		while ((oneByte = zis.read()) != -1) {
	    			fos.write(oneByte);
	    		}
	    		fos.close();
	    		zis.close();
	    		}
	    	catch (IOException e){
	    		System.out.println(e);
	    	}
	    }
    	return 1;
    
    }
	public String readFile(String filename) {
	    String result = "";
	    File fin = new File(filename);
	    // if file exists and is not a directory then return text of file
	    if(fin.exists() && !fin.isDirectory()){
		    try (BufferedReader buffread = new BufferedReader(new FileReader(filename))) {
		        StringBuilder sb = new StringBuilder();
		        String line = buffread.readLine();
		        while (line != null) {
		            sb.append(line);
		            line = buffread.readLine();
		        }
		        result = sb.toString();
		        buffread.close();
		    } catch(Exception e) {
		        e.printStackTrace();
		    } finally{ }
	    }
	    return result;		
	}
	public void writeFile(String filename, Boolean truncateOnOverwrite, Boolean overwrite, String data, Boolean newline, Boolean close){
		File fout = new File(filename);
		// if the file doesn't exist OR it exists and it's not a folder and we ARE to overwrite
		if((!fout.exists()) || (fout.exists() && !fout.isDirectory() && overwrite))
		{
			try {
				if (fout.exists() && overwrite && truncateOnOverwrite){
					// truncate file 
					FileWriter filewrite = new FileWriter(fout,false);
				}
				FileWriter filewrite = new FileWriter(fout,true);
				filewrite.write(data);
				filewrite.flush();
				if (newline) {filewrite.write("\n");}
				if(close){filewrite.flush(); filewrite.close();}
			}
			catch(Exception e){
			}
			finally{ }
		}
		
	}

}
