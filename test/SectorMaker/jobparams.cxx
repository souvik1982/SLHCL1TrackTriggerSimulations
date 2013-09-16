#include "jobparams.h"

//tclap
#include <tclap/CmdLine.h>
using namespace TCLAP;

jobparams::jobparams(int argc, char** argv){
  


   try {
     // command line parser
     CmdLine cmd("Command option", ' ', "0.9");

     ValueArg<int> oeta("a","oeta","eta overlap between sectors (in %)",
			  false, 0, "int");
     cmd.add(oeta);

     ValueArg<int> ophi("b","ophi","phi overlap between sectors (in %)",
			  false, 0, "int");
     cmd.add(ophi);

     ValueArg<bool> efficiencies("c","efficiencies","do we perform the efficiency calculation?",
				 false, 0, "bool");
     cmd.add(efficiencies);   

     ValueArg<std::string> pattfile("d","data","name of the pattern data file",
				   false, "", "string");
     cmd.add(pattfile);

     ValueArg<int> eta("e","eta","how many sectors in eta (bet -2.5 and 2.5)",
			  false, 1, "int");
     cmd.add(eta);

     ValueArg<std::string> testfile("f","fortest","name of the input file used to test",
				    false, "test.root", "string");
     cmd.add(testfile);

     ValueArg<bool> dbg("g","gdb","debug mode (standalone PR used) or not",
			false, 0, "bool");
     cmd.add(dbg);

     ValueArg<std::string> inputfile("i","input","path and name of the input file",
				false, "/scratch/viret/data.root", "string");
     cmd.add(inputfile);

     ValueArg<int> nevt("n","nevt","number of events for the eff test?",
			false, 0, "int");
     cmd.add(nevt);

     ValueArg<std::string> outfile("o","output","name of the output file",
				false, "output.root", "string");
     cmd.add(outfile);

     ValueArg<int> phi("p","phi","how many sectors in phi",
			  false, 8, "int");
     cmd.add(phi);

     ValueArg<bool> rates("r","rates","do we perform the rate calculation? ",
			   false, 0, "bool");
     cmd.add(rates);

     ValueArg<bool> sectors("s","sectors","do we perform the sector calculation?",
			    false, 0, "bool");
     cmd.add(sectors);

     ValueArg<int> test("t","test","do we perform the eff test?",
			false, 0, "bool");
     cmd.add(test);
     


     // parse
     cmd.parse(argc, argv);
     
     m_inputfile    = inputfile.getValue();
     m_outfile      = outfile.getValue();
     m_testfile     = testfile.getValue();
     m_pattfile     = pattfile.getValue();
     m_sectors      = sectors.getValue();
     m_efficiencies = efficiencies.getValue();
     m_rates        = rates.getValue();
     m_test         = test.getValue();
     m_eta          = eta.getValue();
     m_phi          = phi.getValue();
     m_oeta         = oeta.getValue();
     m_ophi         = ophi.getValue();
     m_nevt         = nevt.getValue();
     m_dbg          = dbg.getValue();
   }
   catch (ArgException &e){ // catch exception from parse
     std::cerr << "ERROR: " << e.error() << " for arg " << e.argId()  << std::endl;
     abort();
   }
}

