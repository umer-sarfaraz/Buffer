

#Import Required Modules

import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True
import os
from zipfile import ZipFile
import shutil
from datetime import datetime

#Function Definition and Date-time Retrieval
#Function to write to Log File
#Explanation: The function WriteToLog is defined which takes a string as input. This function is used to retrieve the current system's date and time in a specific format.

def WriteToLog(string):
     
    #Retrieve the current system date time stamp

    now = datetime.now()

    CurrentDay = now.strftime("%d")
    CurrentMonth = now.strftime("%m")
    CurrentYear = now.strftime("%Y")
    time = now.strftime("%H:%M:%S")

#Constructing Log File Name and Path
# Explanation: The code constructs a filename using the string "MissouriOneCall_" and the current date.
#  The filename is updated to replace any colons (":") with underscores ("_"). A file path for the log file is also defined.
    SystemDateTime = CurrentMonth + "_" + CurrentDay + "_" + CurrentYear 
    FileName = "MissouriOneCall_"+SystemDateTime+".txt"
    FileName = FileName.replace(":","_")

    #3. Log File Opening and Writing
    # Explanation: The code checks whether the log file already exists. If it does not, a new file is created and opened in append mode. 
    # The input string along with the system date and time is written to the log file.
    
    LogFilePath = "S:/WL/ScriptLogging/"+FileName
    if(os.path.exists(LogFilePath) == False):
     LogFile = open('S:/WL/ScriptLogging/'+FileName,'a')
    else:
         LogFile = open('S:/WL/ScriptLogging/'+FileName,'a')

    LogFile.write(string + "--" + SystemDateTime + " -- " + time + "\n")


    #Generate FLAG for Creation of Additional Two Buffers (Electric/Fiber and Water/Sewer)

#4. Flag and List Initializations
#Explanation: This code initializes a flag named CreateEF_WS_Buffers as False, which could be used to control the creation of additional buffers later in the code.
#  It also initializes three empty lists - ExtractionList, BufferResultList, 
# and a Boolean variable ProblemFound that could be used to indicate if a problem was encountered during the code execution.


CreateEF_WS_Buffers = False


#Create Initial List Object To Store Extracted Feature Layers

ExtractionList = []
BufferResultList = []

ProblemFound = False


print("***************************************")
print("       Extracting Source Data.....")
print("***************************************\n")

print ("Creating Working File Geodatabase...\n")

#Copy the Original Zip File and Extract It

#5. Extracting Files from a Zip Archive
# Explanation: This code defines the source path of a zip file and the destination where the zip file will be extracted.
#  The zipfile library is used to open and extract the contents of the zip file to the specified location.
#  A message is written to the log file, and a success message is printed to the console.

KBOX_DisasterFiles = "S:\\WL\\Disaster_Recovery\Disaster_Files.zip"
ExtractDestinationFolder = "C:\\Disaster_Recovery"

import zipfile
with zipfile.ZipFile(KBOX_DisasterFiles,"r") as zip_ref:
    zip_ref.extractall(ExtractDestinationFolder)

WriteToLog("Extracting Disaster Recovery Files...")
print("Disaster Files Extracted Successfully!")

 #Generate References to the Source Disaster Recovery File Geodatabases
 #6. Assigning Source Paths
 # Explanation: The code sets up the path for the three disaster recovery file geodatabases for City Data, Fiber, and Electric Data.

DisasterCityFileGDB = "C:\Disaster_Recovery\Disaster_CityData.gdb"
DisasterFiberGDB = "C:\Disaster_Recovery\Disaster_Fiber.gdb"
DisasterElectricGDB = "C:\Disaster_Recovery\Disaster_Electric.gdb"

#Make Directory to Hold the Working File Geodatabase
# 7 Creating Directory for Working File Geodatabase
#Explanation: This code checks if a directory with the name "OneCallBufferCreation" already exists. 
# If it does, it removes the existing directory and then creates a new one. If it does not exist, it simply creates a new directory.


path = "C:\\OneCallBufferCreation\\"
if os.path.exists(path) == True:
     shutil.rmtree(path)
     os.mkdir(path)
else:
      os.mkdir(path)



#8. Creating Working File Geodatabase
#Explanation: This part of the code uses the arcpy module to create a new file geodatabase named "OneCallBuffers.gdb" 
# in the previously created directory. It logs this operation and prints a success message to the console.
print("Generating Working File Geodatabase...")
WorkingFileGDB = "C:\OneCallBufferCreation\OneCallBuffers.gdb"
arcpy.CreateFileGDB_management("C:\OneCallBufferCreation", "OneCallBuffers.gdb")
WriteToLog("Working File GDB Created Successfully ")
print ("Working File GDB Created Successfully!\n")

print("Copying City, Fiber, and Electric Data into Working File Geodatbase...")

#Make a copy of the Required Disaster Recovery Data
#9. Preparing for Data Copy
#Explanation: This part of the code prepares for the data copying process by printing some messages to the console.
#  It also defines the source and destination file paths for the Fiber data.

print("Extracting Fiber Data From Disaster Recovery....\n")
OriginalFiberFC = DisasterCityFileGDB+"\WL_Fiber\Fiber"
WorkingFiberFC = WorkingFileGDB + "\Fiber"


#10. Create City Fiber Feature Layer
# Explanation: This part of the code uses the arcpy module to create a feature layer named "CityFiber_lyr" from the original Fiber feature class.
#  It then selects the features from this layer that match the criteria of UG_OR_OH attribute being 'UG' or NULL.
# The count of the extracted features is retrieved and displayed to the console, and also logged.

arcpy.MakeFeatureLayer_management(OriginalFiberFC, "CityFiber_lyr")
arcpy.SelectLayerByAttribute_management("CityFiber_lyr", "NEW_SELECTION", 
                                         "UG_OR_OH IN ('UG') OR UG_OR_OH IS NULL")
ExtractedFiberCount = arcpy.GetCount_management ("CityFiber_lyr")[0]

print ("Extracted " + str(ExtractedFiberCount)+ " City Fiber Features Successfully!")
WriteToLog("Extracted " + str(ExtractedFiberCount)+ " City Fiber Features Successfully!")

 #Add to Extraction List
 #11. Adding to Extraction List and Copying Features
 #Explanation: The Working Fiber feature class path is added to the ExtractionList. 
 # Then, the features selected in the "CityFiber_lyr" are copied to the working Fiber feature class.
 #  The number of copied features is then counted.

ExtractionList.append(WorkingFiberFC)


arcpy.CopyFeatures_management("CityFiber_lyr", WorkingFiberFC)
CopiedFiberCount = arcpy.GetCount_management ("CityFiber_lyr")[0]

# 12. Verification and Error Handling
# Explanation: The code verifies if the count of extracted features matches the count of copied features.
#  If they match, a success message is printed to the console and logged.
#  If they don't, an error message is displayed and logged, and the ProblemFound flag is set to True.


if(ExtractedFiberCount == CopiedFiberCount):
     print("Successfully Copied ALL Fiber Features into Working File Geodatabse!")
     WriteToLog("Successfully Copied ALL Fiber Features into Working File Geodatabse!")
else:
     print("There was a problem generating the Fiber Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Fiber Features From the Disaster Recovery Source Data")
     ProblemFound = True


#Determine if there were any issues, if so notify, if not continue...
#Explanation: If no problem was found during the previous steps (i.e., ProblemFound is still False), 
# a message is printed to the console indicating the start of the extraction of Fiber Optic Cable data from the Disaster Recovery.

if(ProblemFound == False):
 print("Extracting Fiber Optic Cable Data From Disaster Recovery....\n")
 
 #13. Create Fiber Optic Cable Feature Layer
 # Explanation: This part of the code specifies the path for the original Fiber Optic Cable feature class and the working Fiber Optic Cable feature class. 
 # It then creates a feature layer named "FiberOptic_lyr" from the original Fiber Optic Cable feature class.
 #  Next, it selects the features from this layer that meet certain criteria: the attribute 'OverheadUnderground' is not 'Overhead' 
 # or is NULL, and the 'CableOwner' is 'City' or is NULL. The count of the extracted features is retrieved.
 
 OriginalFiberOpticFC = DisasterFiberGDB+"\FiberOpticCable"
 WorkingFiberOpticCableFC = WorkingFileGDB + "\FiberOpticCable"

 arcpy.MakeFeatureLayer_management(OriginalFiberOpticFC, "FiberOptic_lyr")

 arcpy.SelectLayerByAttribute_management("FiberOptic_lyr", "NEW_SELECTION", 
                                          "(OverheadUnderground <> 'Overhead' OR OverheadUnderground IS NULL) AND (CableOwner = 'City' OR CableOwner IS NULL)")

ExtractedFiberOpticCount = arcpy.GetCount_management ("FiberOptic_lyr")[0]

#14. Copying Features and Error Checking
#Explanation: The features selected in the "FiberOptic_lyr" are copied to the working Fiber Optic Cable feature class.
#  The number of copied features is then counted. If the count of extracted features matches the count of copied features, a success message is printed and logged.
#  If they don't match, an error message is displayed, logged, and the ProblemFound flag is set to True.


arcpy.CopyFeatures_management("FiberOptic_lyr", WorkingFiberOpticCableFC)

CopiedFiberOpticCount = arcpy.GetCount_management (WorkingFiberOpticCableFC)[0]

if(ExtractedFiberOpticCount == CopiedFiberOpticCount):
     print("Successfully Copied ALL Fiber Optic Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Fiber Optic Features into Working File Geodatabase!")

else:
     print("There was a problem generating the Fiber Optic Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Fiber Optic Features From the Disaster Recovery Source Data")
     ProblemFound = True

#15.  Logging and Preparing for Next Step
# Explanation: The number of successfully extracted Fiber Optic Cable features is printed and logged. 
# The working Fiber Optic Cable feature class path is added to the ExtractionList. 
# The code then checks if any problems were found in the previous steps. 
# If no problems were found (ProblemFound is False), it proceeds to the creation of the PW Fiber Optic Cable feature layer.

print ("Extracted " + str(ExtractedFiberOpticCount)+ " City Fiber Optic Cable Features Successfully!")
WriteToLog("Extracted " + str(ExtractedFiberOpticCount)+ " City Fiber Optic Cable Features Successfully!")

#Add to Extraction List

ExtractionList.append(WorkingFiberOpticCableFC)


#Create PW Fiber Optic Cable Feature Layer

if(ProblemFound == False):
 
 # 16. Creating Feature Layers and Extracting Features
 # Explanation: The original feature file is loaded from the file path defined in DisasterFiberGDB, and a working feature file path is defined in WorkingFileGDB.
 #  A new feature layer named Feature_lyr is created from the original feature.
 #  The script then counts the number of features in the layer and copies them into the working feature file. The number of features copied to the working file is also counted.

 #Note: For San_Lines, wLateralLine, and wPressurizedMain,  # the layer is created with a selection applied, 
 # choosing the features where the Owner field equals 'City' or is NULL, and for wLateralLine, the Private field should not equal 'Yes'.

 OriginalPWFiberOpticFC = DisasterFiberGDB+"\PW_streets\PW_Fiber_Optic_Cable"
 WorkingPWFiberOpticCableFC = WorkingFileGDB + "\PW_FiberOpticCable"

 arcpy.MakeFeatureLayer_management(OriginalPWFiberOpticFC, "PWFiberOptic_lyr")

 ExtractedPWFiberOpticCount = arcpy.GetCount_management ("PWFiberOptic_lyr")[0]


 arcpy.CopyFeatures_management("PWFiberOptic_lyr", WorkingPWFiberOpticCableFC)

 CopiedPWFiberOpticCount = arcpy.GetCount_management (WorkingPWFiberOpticCableFC)[0]

 #17. Error Checking
 #  Explanation: The script checks if the number of features extracted from the original layer equals the number of features copied into the working feature file.
 #  If they match, it prints and logs a success message. If they don't match, it prints and logs an error message and sets the ProblemFound flag to True.

 if(ExtractedPWFiberOpticCount == CopiedPWFiberOpticCount):
     print("Successfully Copied ALL Public Works Fiber Optic Features into Working File Geodatabse!")
     WriteToLog("Successfully Copied ALL Public Works Fiber Optic Features into Working File Geodatabse!")
 else:
     print("There was a problem generating the Fiber Optic Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Fiber Optic Features From the Disaster Recovery Source Data")
     ProblemFound = True

# 18. Logging and Preparing for Next Step
# Explanation: The number of successfully extracted features is printed and logged. The working feature class path is added to the ExtractionList.
#  The script then checks if any problems were found in the previous steps. 
# If no problems were found (ProblemFound is False), it proceeds to the next feature extraction process.

 print ("Extracted " + str(ExtractedPWFiberOpticCount)+ " Public Works Fiber Optic Cable Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedPWFiberOpticCount)+ " Public Works Fiber Optic Cable Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingPWFiberOpticCableFC)


#Create PrimaryUGLineSection Feature Layer (No Filter To Be Applied)

if(ProblemFound == False):
 
 #same as 16


 OriginalPrimaryUGLineSectionFC = DisasterElectricGDB+"\PrimaryUGLineSection"
 WorkingPrimaryUGLineSectionFC = WorkingFileGDB + "\PrimaryUGLineSection"

 arcpy.MakeFeatureLayer_management(OriginalPrimaryUGLineSectionFC, "PrimaryUGLineSection_lyr")


 ExtractedPrimaryUGLineSectionCount = arcpy.GetCount_management ("PrimaryUGLineSection_lyr")[0]


 arcpy.CopyFeatures_management("PrimaryUGLineSection_lyr", WorkingPrimaryUGLineSectionFC)

 CopiedPrimaryUGLineSectionFCCount = arcpy.GetCount_management (WorkingPrimaryUGLineSectionFC)[0]

  #same as 17

 if(ExtractedPrimaryUGLineSectionCount == CopiedPrimaryUGLineSectionFCCount):
     print("Successfully Copied ALL Primary Underground Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Primary Underground Features into Working File Geodatabase!")
 else:
     print("There was a problem generating the Primary Underground Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Primary Underground Features From the Disaster Recovery Source Data")
     ProblemFound = True

 #same as 18

 print ("Extracted " + str(ExtractedPrimaryUGLineSectionCount)+ " City PrimaryUGLineSection Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedPrimaryUGLineSectionCount)+ " City PrimaryUGLineSection Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingPrimaryUGLineSectionFC)

if(ProblemFound == False):
 
  #same as 16

 #Create SecondaryUGLineSection Feature Layer (No Filter To Be Applied)

 OriginalSecondaryUGLineSectionFC = DisasterElectricGDB+"\SecondaryUGLineSection"
 WorkingSecondaryUGLineSectionFC = WorkingFileGDB + "\SecondaryUGLineSection"


 arcpy.MakeFeatureLayer_management(OriginalSecondaryUGLineSectionFC, "SecondaryUGLineSection_lyr")


 ExtractedSecondaryUGLineSectionCount = arcpy.GetCount_management ("SecondaryUGLineSection_lyr")[0]




 arcpy.CopyFeatures_management("SecondaryUGLineSection_lyr", WorkingSecondaryUGLineSectionFC)

 CopiedSecondaryUGLineSectionFCCount = arcpy.GetCount_management (WorkingSecondaryUGLineSectionFC)[0]

  #same as 17

 if(ExtractedSecondaryUGLineSectionCount == CopiedSecondaryUGLineSectionFCCount):
     print("Successfully Copied ALL Secondary Underground Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Secondary Underground Features into Working File Geodatabase!")
 else:
     print("There was a problem generating the Secondary Underground Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Secondary Underground Features From the Disaster Recovery Source Data")
     ProblemFound = True

 #same as 18

 print ("Extracted " + str(ExtractedSecondaryUGLineSectionCount)+ " City SecondaryUGLineSection Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedSecondaryUGLineSectionCount)+ " City SecondaryUGLineSection Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingSecondaryUGLineSectionFC)

if(ProblemFound == False):


 #Create Sanitary Sewer Feature Layer

  #same as 16

 OriginalSanitarySewerFC = DisasterCityFileGDB+"\PW_sewer\San_Lines"
 WorkingSanitarySewerFC = WorkingFileGDB + "\San_Lines"

 arcpy.MakeFeatureLayer_management(OriginalSanitarySewerFC, "OriginalSanitarySewer_lyr")

 arcpy.SelectLayerByAttribute_management("OriginalSanitarySewer_lyr", "NEW_SELECTION", 
                                          "Owner = 'City' OR Owner IS NULL")


 ExtractedSanitarySewerCount = arcpy.GetCount_management ("OriginalSanitarySewer_lyr")[0]


 arcpy.CopyFeatures_management("OriginalSanitarySewer_lyr", WorkingSanitarySewerFC)

 CopiedSanitarySewerFCCount = arcpy.GetCount_management (WorkingSanitarySewerFC)[0]
 #same as 17

 if(ExtractedSanitarySewerCount == CopiedSanitarySewerFCCount):
     print("Successfully Copied ALL Sanitary Sewer Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Sanitary Sewer Features into Working File Geodatabase!")
 else:
     print("There was a problem generating the Sanitary Sewer Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Sanitary Sewer Features From the Disaster Recovery Source Data")
     ProblemFound = True

 #same as 18

 print ("Extracted " + str(ExtractedSanitarySewerCount)+ " City San_Lines Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedSanitarySewerCount)+ " City San_Lines Features Successfully!")


 #Add to Extraction List

 ExtractionList.append(WorkingSanitarySewerFC)


#Create Lateral Lines Feature Layer

if(ProblemFound == False):
 
  #same as 16

 OriginalLateralLineFC = DisasterCityFileGDB+"\Water_Network\wLateralLine"
 WorkingLateralLineFC = WorkingFileGDB + "\wLateralLine"

 arcpy.MakeFeatureLayer_management(OriginalLateralLineFC, "OriginalLateralLine_lyr")

 arcpy.SelectLayerByAttribute_management("OriginalLateralLine_lyr", "NEW_SELECTION", 
                                          "Private <> 'Yes'")


 ExtractedLateralLineCount = arcpy.GetCount_management ("OriginalLateralLine_lyr")[0]


 arcpy.CopyFeatures_management("OriginalLateralLine_lyr", WorkingLateralLineFC)

 CopiedLateralLineFCCount = arcpy.GetCount_management (WorkingLateralLineFC)[0]

 #same as 17

 if(ExtractedLateralLineCount == CopiedLateralLineFCCount):
     print("Successfully Copied ALL Lateral Line Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Lateral Line Features into Working File Geodatabase!")
 else:
     print("There was a problem generating the Lateral Line Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Lateral Line Features From the Disaster Recovery Source Data")
     ProblemFound = True


 #same as 18
 print ("Extracted " + str(ExtractedLateralLineCount)+ " City LateralLine Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedLateralLineCount)+ " City LateralLine Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingLateralLineFC)


#Create Pressurized Mains Feature Layer

if(ProblemFound == False):


 #same as 16

 OriginalPressurizedMainsFC = DisasterCityFileGDB+"\Water_Network\wPressurizedMain"
 WorkingPressurizedMainsFC = WorkingFileGDB + "\wPressurizedMain"


 arcpy.MakeFeatureLayer_management(OriginalPressurizedMainsFC, "wPressurizedMain_lyr")

 arcpy.SelectLayerByAttribute_management("wPressurizedMain_lyr", "NEW_SELECTION", 
                                          "Owner='City' OR Owner IS NULL")


 ExtractedPressurizedMainCount = arcpy.GetCount_management ("wPressurizedMain_lyr")[0]


 arcpy.CopyFeatures_management("wPressurizedMain_lyr", WorkingPressurizedMainsFC)

 CopiedPressurizedMainsFCCount = arcpy.GetCount_management (WorkingPressurizedMainsFC)[0]

 #same as 17

 if(ExtractedPressurizedMainCount == CopiedPressurizedMainsFCCount):
     print("Successfully Copied ALL Pressurized Main Features into Working File Geodatabse!")
     WriteToLog("Successfully Copied ALL Pressurized Main Features into Working File Geodatabse!")

 else:
     print("There was a problem generating the Pressurized Main Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Pressurized Main Features From the Disaster Recovery Source Data")
     ProblemFound = True

 #same as 18

 print ("Extracted " + str(ExtractedPressurizedMainCount)+ " City Pressurized Main Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedPressurizedMainCount)+ " City Pressurized Main Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingPressurizedMainsFC)

if(ProblemFound == False):

 print("*********************************************")
 print("       Generating Intial Utility Buffers.....")
 print("*******************************************\n")


# 19. This part of the script processes each feature class in the ExtractionList. It counts the number of features in each class, prints out a start message,
#  runs a buffer analysis on each class, and adds the resulting buffered feature class to the BufferResultList.
BufferResultList = []

FCCount = 0
for FC in ExtractionList:
     count = arcpy.GetCount_management(FC)[0]
     lastindex = FC.rfind('\\')
     FCCount = FCCount+ 1

     print("Buffering " + str(count) + " " + FC[lastindex+1:] + " Features...")

     BufferFC = arcpy.Buffer_analysis(FC, WorkingFileGDB+"\\"+FC[lastindex+1:] + "_Buffer", "100 Feet", "FULL", 
                       "ROUND", "ALL", "","PLANAR")

     print ("Buffer Completed for " + str(FC[lastindex+1:]) + " Feature Class")
     WriteToLog("Buffer Completed for " + str(FC[lastindex+1:]) + " Feature Class")

     #Add it to the Buffer Result List in Prep for Final Merge

    

     BufferResultList.append(BufferFC)

    
 #Loop through the Buffer Results and Merge Them
 # 20. This part of the script merges all the buffered feature classes into one layer. 
 # If the CreateEF_WS_Buffers flag is set to true, it will also create two additional merged buffers: one for electric/fiber and another for water/sewer.

print("Combining Buffer Polygons into Single Layer for Processing...\n")
WriteToLog("Combining Buffer Polygons into Single Layer for Processing...")
Fiber_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\Fiber_Buffer"
FiberOpticCable_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\FiberOpticCable_Buffer"
PrimaryUGLineSection_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PrimaryUGLineSection_Buffer"
PW_FiberOpticCable_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PW_FiberOpticCable_Buffer"
San_Lines_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\San_Lines_Buffer"
SecondaryUGLineSection_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\SecondaryUGLineSection_Buffer"
wLateralLine_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wLateralLine_Buffer"
wPressurizedMain_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wPressurizedMain_Buffer"
MergedBuffers = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\MergedBuffers"



#Include a script parameter to also generate two additional buffer outputs
#1. Electric/Fiber
#2. Water/Sewer

if(CreateEF_WS_Buffers == True):
   arcpy.Merge_management(inputs="Fiber_Buffer;FiberOpticCable_Buffer;PW_FiberOpticCable_Buffer;PrimaryUGLineSection_Buffer;SecondaryUGLineSection_Buffer", output="C:/OneCallBufferCreation/OneCallBuffers.gdb/EF_Buffers", field_mappings='SHAPE_Length "SHAPE_Length" false true true 8 Double 0 0 ,First,#,Fiber_Buffer,SHAPE_Length,-1,-1,FiberOpticCable_Buffer,Shape_Length,-1,-1,PW_FiberOpticCable_Buffer,Shape_Length,-1,-1,PrimaryUGLineSection_Buffer,Shape_Length,-1,-1,SecondaryUGLineSection_Buffer,Shape_Length,-1,-1;SHAPE_Area "SHAPE_Area" false true true 8 Double 0 0 ,First,#,Fiber_Buffer,SHAPE_Area,-1,-1,FiberOpticCable_Buffer,Shape_Area,-1,-1,PW_FiberOpticCable_Buffer,Shape_Area,-1,-1,PrimaryUGLineSection_Buffer,Shape_Area,-1,-1,SecondaryUGLineSection_Buffer,Shape_Area,-1,-1')
   arcpy.Merge_management(inputs="San_Lines_Buffer;wPressurizedMain_Buffer;wLateralLine_Buffer", output="C:/OneCallBufferCreation/OneCallBuffers.gdb/WS_Buffers", field_mappings='Shape_Length "Shape_Length" false true true 8 Double 0 0 ,First,#,San_Lines_Buffer,Shape_Length,-1,-1,wPressurizedMain_Buffer,Shape_Length,-1,-1,wLateralLine_Buffer,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0 ,First,#,San_Lines_Buffer,Shape_Area,-1,-1,wPressurizedMain_Buffer,Shape_Area,-1,-1,wLateralLine_Buffer,Shape_Area,-1,-1')
 
# Create Merged Buffers for Missouri One Call
arcpy.Merge_management("C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\Fiber_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\FiberOpticCable_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PrimaryUGLineSection_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PW_FiberOpticCable_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\San_Lines_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\SecondaryUGLineSection_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wLateralLine_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wPressurizedMain_Buffer", MergedBuffers, "SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\Fiber_Buffer,SHAPE_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\FiberOpticCable_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PrimaryUGLineSection_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PW_FiberOpticCable_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\San_Lines_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\SecondaryUGLineSection_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wLateralLine_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wPressurizedMain_Buffer,Shape_Length,-1,-1;SHAPE_Area \"SHAPE_Area\" false true true 8 Double 0 0 ,First,#,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\Fiber_Buffer,SHAPE_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\FiberOpticCable_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PrimaryUGLineSection_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PW_FiberOpticCable_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\San_Lines_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\SecondaryUGLineSection_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wLateralLine_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wPressurizedMain_Buffer,Shape_Area,-1,-1")
print("Process Complete!\n")

#21 This part of the script merges all the buffered feature classes into one layer. If the CreateEF_WS_Buffers flag is set to true,
#  it will also create two additional merged buffers: one for electric/fiber and another for water/sewer.


#Copy the Modified Snow Grid into Working File GDB

print("Gathering the Snow Grid for Page Name Assignment....")
ModifiedSnowGrid = "S:\WL\MarkRees\OneCallBufferCreation\All_Utilities_Buffers.gdb\Modified_Snow_Grid"
arcpy.CopyFeatures_management(ModifiedSnowGrid, WorkingFileGDB+"\Modified_Snow_Grid")
print("Modified Snow Grid Copied Successfully!...")
WriteToLog("Modified Snow Grid Copied Successfully!...")

#22. This last part of the script dissolves the merged buffers into one polygon, and prints a success message. 
# The dissolve process is often used to merge overlapping or adjacent polygons into a single feature. 
# This can be useful in situations where you need to aggregate data or reduce the complexity of the data.

#Merge the Buffers

DissolvedBuffers = WorkingFileGDB+"\DissolvedBuffers"
print("Dissolving Buffers into One Polygon....")
WriteToLog("Dissolving Buffers into One Polygon....")
arcpy.Buffer_analysis(MergedBuffers, DissolvedBuffers, "1 Feet", "FULL", "ROUND", "ALL", "", "PLANAR")
print("Dissolve Process Completed Successfully!")


#Loop through the Input Feature Classes and Check if ALL Features are found within a Buffer
# 23. This segment of the code iterates over each feature class in the ExtractionList, creates a temporary feature layer, 
# and performs a spatial selection on that layer to select only the features that are completely within the dissolved buffer. 
# The total number of features in the feature class and the number of features selected by the location query are printed and logged.
# A loop begins to iterate over each feature class in the ExtractionList.
for FC in ExtractionList:
    # Prints a log message indicating the start of the selection process for the current feature class.
    print("Selecting Features From Feature Class " + FC + " Inside Buffer Polygons...")
    WriteToLog("Selecting Features From Feature Class " + FC + " Inside Buffer Polygons...")
    # The MakeFeatureLayer_management function is used to create a temporary feature layer from the feature class.
    arcpy.MakeFeatureLayer_management(FC,"FLayer")

    # Counts the number of features in the created feature layer.
    NumFeatures = int(arcpy.GetCount_management("FLayer")[0])
     # The SelectLayerByLocation_management function is used to select features in the temporary feature layer that are completely within the dissolved buffer.
    arcpy.SelectLayerByLocation_management("FLayer", "COMPLETELY_WITHIN", DissolvedBuffers, "", "NEW_SELECTION", "NOT_INVERT")
    # Counts the number of features selected by the above operation.
    NumInsideBuffer = arcpy.GetCount_management("FLayer")

    # Prints and logs the total number of features in the feature class and the number of features selected by the location query.

    print("The Number of Features in " + FC + " are : " + str(NumFeatures) + " The Number of Features Within Buffer were " + str(int(NumInsideBuffer[0])) )
    WriteToLog("The Number of Features in " + FC + " are : " + str(NumFeatures) + " The Number of Features Within Buffer were " + str(int(NumInsideBuffer[0])))

#24. This section of the script first defines a spatial reference object, which is a specific coordinate system. 
# In this case, it's "NAD 1983 StatePlane Missouri Central FIPS 2402 (US Feet)". Then, it creates a new feature dataset in the 
# geodatabase at the specified path, which will be used to store the output buffers. The spatial reference object is 
# assigned to this new feature dataset, and a message about the successful creation and application of the spatial reference is printed and logged.

#Create a Feature Dataset to Hold the Exploded Buffer Feature Classes
# Prints a message indicating the start of the spatial reference information gathering process.
print("Gathering Spatial Reference Information...")
# Creates a spatial reference object.
destination_spatialref = arcpy.CreateSpatialReference_management("NAD 1983 StatePlane Missouri Central FIPS 2402 (US Feet)")
# Creates a feature dataset in the specified geodatabase with the created spatial reference.
arcpy.CreateFeatureDataset_management("C:/OneCallBufferCreation/OneCallBuffers.gdb", "OutputBuffers", destination_spatialref)
# Prints and logs a message indicating the successful application of the spatial reference information to the feature dataset.
print("Spatial Reference Information Applied to Buffer Feature Dataset...")
WriteToLog("Spatial Reference Information Applied to Buffer Feature Dataset...")

#Create a Feature Dataset to Hold the Final Buffer Feature Classes

#25. This block is creating a new Feature Dataset in the "C:/OneCallBufferCreation/OneCallBuffers.gdb" Geodatabase named "OutputBuffers" 
# and is assigning it a spatial reference ("NAD 1983 StatePlane Missouri Central FIPS 2402 (US Feet)"). 
# A Feature Dataset is a collection of related feature classes that share a common spatial reference.

# A message is printed to indicate the start of the spatial reference information gathering process.
print("Gathering Spatial Reference Information...")
WriteToLog("Gathering Spatial Reference Information...")
# The spatial reference is set.
destination_spatialref = arcpy.CreateSpatialReference_management("NAD 1983 StatePlane Missouri Central FIPS 2402 (US Feet)")
 #A feature dataset is created in the specified file geodatabase with the set spatial reference. 
arcpy.CreateFeatureDataset_management("C:/OneCallBufferCreation/OneCallBuffers.gdb", "FinalBuffers", destination_spatialref)
print("Spatial Reference Information Applied to Buffer Feature Dataset...")
WriteToLog("Spatial Reference Information Applied to Buffer Feature Dataset...")

#This section of the code starts with adding a field to the dissolved buffers, splitting the dissolved buffers using a modified snow grid, 
# assigning page names to the buffers, creating output shapefiles, and setting up a template feature class.

#Add the MAPPREF field to the Dissolved Buffers Feature Class
## A new field, MAPPREF, is added to the dissolved buffers feature class. The field type is set to "TEXT", with a field length of 29 characters.
arcpy.AddField_management(DissolvedBuffers, "MAPPREF", "TEXT", "", "", "29", "", "NULLABLE", "NON_REQUIRED", "")
#AddField_management is a function from the arcpy module that adds a new field to a table or a feature class. In this case, a text field named "MAPPREF" 
# is being added to the DissolvedBuffers feature class.


#Split_analysis function is used to divide the DissolvedBuffers feature class based on the boundaries of polygons in Modified_Snow_Grid. 
# The PageName field is used to name the resultant features.
# #Perform the Split Polygons Using the Modified Snow Grid

# A message is printed and logged to indicate that the script is starting to create individual buffers based on the snow grid position.
print("Creating Individual Buffers Based on Snow Grid Position....")
WriteToLog("Creating Individual Buffers Based on Snow Grid Position....")
# The SnowGridRef variable is set to the location of the modified snow grid.
SnowGridRef = WorkingFileGDB+"\Modified_Snow_Grid"
# The dissolved buffers are split using the modified snow grid. The "PageName" field is used for the split. The output is stored in the specified workspace.
arcpy.Split_analysis(in_features=DissolvedBuffers, split_features=SnowGridRef, split_field="PageName", out_workspace="C:/OneCallBufferCreation/OneCallBuffers.gdb/OutputBuffers", cluster_tolerance="")
print("Process Complete!..")
WriteToLog("Process Complete!..")

#Assign Page Name to the Buffer Feature Classes


#The os and shutil libraries are being used to manage files and directories on the system. 
# os.path.exists checks if the specified path exists, shutil.rmtree deletes an entire directory tree, and os.mkdir creates a directory.

# The workspace environment is set
env.workspace = "C:/OneCallBufferCreation/OneCallBuffers.gdb/OutputBuffers"
# The overwriteOutput environment setting is set to True to overwrite existing files.
arcpy.env.overwriteOutput = True
# The specified directory is checked if it exists. If it does, it is deleted and recreated. If it doesn't exist, it is created.
path = "C:\\OneCallShapeFiles\\"
if os.path.exists(path) == True:
     shutil.rmtree(path)
     os.mkdir(path)
else:
      os.mkdir(path)

#arcpy.ListFeatureClasses() returns a list of the feature classes in the current workspace.

#Create FinalTemp Feature Class
# Messages are printed and logged to indicate that the script is starting to write output shapefiles and transfer PageName field values.
print("Writing Output Shapefiles....")
WriteToLog("Writing Output Shapefiles....")
print("Transferring PageName Field Values....")
WriteToLog("Transferring PageName Field Values....")
# A list of all the feature classes in the current workspace is obtained.
FCList = arcpy.ListFeatureClasses()
# The count and appendcount variables are initialized.
count = 0
appendcount = 0

#arcpy.ImportXMLWorkspaceDocument_management is used to import an XML workspace document into a target geodatabase. 
# In this case, the schema of the template feature class is being imported from an XML file named "SHAPEFILETEMPLATE.XML".
# The schema includes information about the structure of the feature class, such as the fields and their properties, but not the actual data.

#Create the Feature Class Template
# A message is printed and logged to indicate that the script is generating a template feature class.
print ("Generating Template Feature Class.....")
WriteToLog("Generating Template Feature Class.....")
# A template feature class is imported from an XML workspace document.
arcpy.ImportXMLWorkspaceDocument_management(target_geodatabase="C:/OneCallBufferCreation/OneCallBuffers.gdb", in_file="S:\\WL\\MarkRees\\OneCallBufferCreation\\SHAPEFILETEMPLATE.XML", import_type="SCHEMA_ONLY", config_keyword="")
print ("Template Feature Class Generated Successfully!")
WriteToLog("Template Feature Class Generated Successfully!")


# Last Phase of the code
#This block of code involves several steps: looping through feature classes in a list, performing identity analysis, 
# calculating a new field, appending the results into a template feature class, renaming fields to comply with Shapefile standards, 
# converting the feature class to a shapefile, and performing geometry repairs and checks. Lastly, it packages the final output into a ZIP file.

# Loops through each feature class (FC) in the FCList

#The Identity_analysis function performs an identity operation, which computes the geometric intersection of two input datasets. 
# In this case, it intersects the A1 and SnowGridRef datasets and writes the output to outfc.
for BuffFC in FCList:
     A1 = BuffFC
     count = count + 1
     appendcount = appendcount + 1
    
    
     # Perform a spatial join between each FC and the SnowGridRef.
     # Process: Spatial Join
     outfc = BuffFC+ "_Final"
     print("Performing Identity " + str(appendcount)+ " to Transfer PageName....")
     WriteToLog("Performing Identity " + str(appendcount)+ " to Transfer PageName....")
     arcpy.Identity_analysis(A1,SnowGridRef, outfc,"ALL", cluster_tolerance="", relationship="NO_RELATIONSHIPS")
     print("Identity Operation Successfull!...")
     WriteToLog("Identity Operation Successfull!...")
                            
    
     #Calculate MAPPREF field to match PageName
     
     #The CalculateField_management function is used to calculate the values of a field. Here, it sets the MAPPREF field to match the PageName field. 
     # The Append_management function is used to append multiple datasets of the same data type into an existing dataset.
     
     ## Set the MAPPREF field to match the PageName field
     arcpy.CalculateField_management(outfc, "MAPPREF", "!PageName!", "PYTHON_9.3", "#")


     #Append into the Template Feature Class
     # Append the current FC to a feature class in the OneCallBuffers geodatabase.    
     arcpy.Append_management(outfc, "C:\OneCallBufferCreation\OneCallBuffers.gdb\TempFC","NO_TEST")
    
     print(str(appendcount) + " Buffer Polygon Features Appended into Template Feature Class Succesffully....")
     WriteToLog(str(appendcount) + " Buffer Polygon Features Appended into Template Feature Class Succesffully....")


#Rename the fields Before Converting to Shapefile...

import arcpy

TempFC = "C:\OneCallBufferCreation\OneCallBuffers.gdb\TempFC"

#This part of the script iterates over each field in the TempFC feature class and renames the field if it contains 'PageName'
#  in the field name and its length is greater than or equal to 10. The AlterField_management function is used to modify the properties of a table field.

#Rename the fields Before Converting to Shapefile...

# Create a list of all fields in the TempFC feature class.
fieldlist = arcpy.ListFields(TempFC)

# Iterate through the field list and rename any fields with 'PageName' in the name and a length of 10 or more characters.
for field in fieldlist:
     fieldname = str(field.name)
    
     fieldlength = len(fieldname)
     if fieldlength >= 10 and 'PageName' in fieldname:
         newname = fieldname.replace("PageName","Page")
         arcpy.AlterField_management(TempFC, fieldname, newname, newname)
print ("Fields Renamed to Shapefile Standard....")
WriteToLog("Fields Renamed to Shapefile Standard....")

#The DefineProjection_management function is used to define the coordinate system of a dataset to match a spatial reference. 
# The FeatureClassToShapefile_conversion function is used to convert a feature class into a shapefile. RepairGeometry_management
# is used to check and repair issues with the geometric data. The AddSpatialIndex_management function is used to add a spatial index to an existing dataset.

#Convert to Final Shapefile For Delivery
print("Converting Feature Class to Delivery Shapefile...")
WriteToLog("Converting Feature Class to Delivery Shapefile...")


#Define Spatial Reference
spatial_ref = arcpy.Describe(TempFC).spatialReference
arcpy.DefineProjection_management(TempFC, spatial_ref)


arcpy.FeatureClassToShapefile_conversion(TempFC,"C:\OneCallBufferCreation")
print ("Delivery Shapefile Generated....")
WriteToLog("Delivery Shapefile Generated....")


#Repair Geometry (Do not delete null values option

print ("Repairing Geometry.....")
arcpy.RepairGeometry_management(in_features="C:\OneCallBufferCreation\TempFC.shp", delete_null="KEEP_NULL")
WriteToLog("Repairing Geometry.....")
  
# #Add Spatial Index

print ("Buidling Spatial Index....")
WriteToLog("Buidling Spatial Index....")
arcpy.AddSpatialIndex_management("C:\OneCallBufferCreation\TempFC.shp")

#CheckGeometry_management function checks the geometry of the dataset and outputs a table with errors, if any. 
# This table is then examined to see if any issues were discovered during the check.

#Perform Check Geometry

print ("Checking Geometry for Errors....")
WriteToLog("Checking Geometry for Errors....")
CheckTable = "C:/OneCallBufferCreation/OneCallBuffers.gdb/GeometryCheckResult"
if os.path.exists(CheckTable) == True:
     os.remove(CheckTable)
arcpy.CheckGeometry_management(in_features="C:\OneCallBufferCreation\TempFC.shp", out_table="C:/OneCallBufferCreation/OneCallBuffers.gdb/GeometryCheckResult")


#Check the number of rows in the Check Geometry Result

result = arcpy.GetCount_management(CheckTable)
rowcount = int(result.getOutput(0))
if rowcount > 0:
     print ("Geometry Issues Discovered in Final Output...Please Review")
     WriteToLog("Geometry Issues Discovered in Final Output...Please Review")
else:
     print ("Geometry Check Successfull! Final Output ZIP OK for Delivery!")
     WriteToLog("Geometry Check Successfull! Final Output ZIP OK for Delivery!")

#DefineProjection_management is used again to ensure that the shapefile is associated with the correct projection.    

#Define Projection (Ensure PRJ associated with ShapeFile

print("Associating Correct Projection to Shapefile....")
WriteToLog("Associating Correct Projection to Shapefile....")
arcpy.DefineProjection_management(in_dataset="C:\\OneCallBufferCreation\\TempFC.shp", coor_system="PROJCS['NAD_1983_StatePlane_Missouri_Central_FIPS_2402_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1640416.666666667],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-92.5],PARAMETER['Scale_Factor',0.9999333333333333],PARAMETER['Latitude_Of_Origin',35.83333333333334],UNIT['Foot_US',0.3048006096012192]]")



#n the final section, the script renames the output shapefile, deletes an old zip file if it exists, and creates a new one with the current output.
#  The resulting ZIP file contains all necessary files related to the shapefile (.cpg, .dbf, .prj, .shp, .shp.xml, .shx), 
# which are written using the ZipFile class from the zipfile module. The ZIP file is then closed, and a message is logged and printed 
# indicating the successful generation of the ZIP file.

print("Creating ZIP File for Delivery..." ) 
WriteToLog("Creating ZIP File for Delivery...")


#Rename the Shapefile before Compression to ZIP
print("Renaming Shapefile Before Final Packaging...")
WriteToLog("Renaming Shapefile Before Final Packaging...")
arcpy.Rename_management("C:\\OneCallBufferCreation\\TempFC.shp","UtilityBuffer.shp")
print("Rename Successfull!")
WriteToLog("Rename Successfull!")

zippath = "C:\\OneCallBufferCreation\\UtilityBuffers.zip"
if os.path.exists(zippath) == True:
     os.remove(zippath)
zipObj = ZipFile("C:\\OneCallBufferCreation\\UtilityBuffers.zip", 'w')
# Add multiple files to the zip
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.cpg')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.dbf')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.prj')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.shp')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.shp.xml')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.shx')
                 
# close the Zip File
zipObj.close()

WriteToLog("Final Output Buffer Shapefile ZIP Generated Successfully!..")
print("Final Output Buffer Shapefile ZIP Generated Successfully!..")
