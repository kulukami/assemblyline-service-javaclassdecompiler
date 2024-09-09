import os
import sys
import subprocess

from assemblyline_v4_service.common.base import ServiceBase
from assemblyline_v4_service.common.request import MaxExtractedExceeded, ServiceRequest
from assemblyline_v4_service.common.result import Result, ResultTextSection

os.environ["JAVA_HOME"]="/opt/al_service/jdk"

class JavaClassDecompiler(ServiceBase):
    def __init__(self, config=None):
        super().__init__(config)

    def execute(self, request: ServiceRequest) -> None:
        result = Result()
        request.result = result
        summary_section_heuristic = None
        extracted = []

        main_section = ResultTextSection("Decompiling Java.class")
        result.add_section(main_section)

        if request.file_type == "java/class":
            extracted = self.extract_javaclass(request)
            summary_section_heuristic = 1
        else:
            not_found = ResultTextSection("not a java/class", auto_collapse=True)
            main_section.add_subsection(not_found)
            return None

        if extracted == None or len(extracted) ==0:
            not_found = ResultTextSection("extracted nothing", auto_collapse=True)
            main_section.add_subsection(not_found)
            return None
    
        listing = ResultTextSection("Listing Java.class code", auto_collapse=True)
        main_section.add_subsection(listing)

        if summary_section_heuristic:
            listing.set_heuristic(summary_section_heuristic)
        
        for files in extracted:
            try:
                listf = ResultTextSection(files[1], auto_collapse=True)
                listing.add_subsection(listf)
                request.add_extracted(files[0], files[1], "decompiled from Java.class")
            except MaxExtractedExceeded:
                main_section.add_line(
                    "Maximum number of extracted files reached - not all were decompiled"
                )
                break


    def extract_javaclass(self, request: ServiceRequest):
        """Will attempt to use cfr to extract a decompiled .java code from a compiled java.class"""
        
        extracted = []
        JVMCores = self.config.get("JavaActiveProcessorCount", 2)
        JavaXmsM = self.config.get("JavaXmsM", 64)
        JavaXmxM = self.config.get("JavaXmxM", 256)
        javabin =  os.path.join(os.getcwd(), "jdk","bin", "java")
        cfrpath =  os.path.join(os.getcwd(), "cfr","cfr-0.152.jar")
        jvmcores = "-XX:ActiveProcessorCount={}".format(JVMCores)

        _ = subprocess.run(
            [ javabin, jvmcores, "-Xms{}m".format(JavaXmsM), "-Xmx{}m".format(JavaXmxM), 
            "-jar", cfrpath, request.file_path,
            "--outputdir", os.path.join(self.working_directory, "class_output") ,
            ],
            env=os.environ,
            capture_output=True,
            check=False,
        )

        for (d1,d2,f1) in os.walk(os.path.join(self.working_directory, "class_output")) :
            for each_f in f1:
                if each_f.endswith(".java"):
                    extracted.append([os.path.join(self.working_directory,"class_output",d1,each_f), each_f, sys._getframe().f_code.co_name])
        return extracted

    # ./jdk/bin/java path/to/target.class -Xms64m -Msx256m --outputdir class_output -jar cfr/cfr-0.152.jar
