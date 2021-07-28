#include "G4NeutronReweighter.hh"

G4NeutronReweighter::G4NeutronReweighter(TFile * totalInput, TFile * FSInput, std::map< std::string, TGraph* > &FSScales){
  fInelastic = "neutronInelastic";
  theInts = {"piprod", "abs", "pprod","inel"};
  Initialize(totalInput, FSInput, FSScales);
}

G4NeutronReweighter::G4NeutronReweighter(TFile * totalInput, TFile * FSInput, const std::map< std::string, TH1D* > &FSScales, TH1D * inputElasticBiasHist){
  fInelastic = "neutronInelastic";
  theInts = {"piprod", "abs", "pprod","inel"};
  Initialize(totalInput,FSInput,FSScales,inputElasticBiasHist);
}

std::string G4NeutronReweighter::GetInteractionSubtype( G4ReweightTraj & theTraj ){
    int nPi0     = theTraj.HasChild(111).size();
    int nPiPlus  = theTraj.HasChild(211).size();
    int nPiMinus = theTraj.HasChild(-211).size();
    int nProton = theTraj.HasChild(2212).size();
    int nNeutron = theTraj.HasChild(2112).size();

    if( (nPi0 + nPiPlus + nPiMinus) > 0){
      return "piprod";
    }
    else if(nProton == 0 && nNeutron == 0 && (nPi0 + nPiPlus + nPiMinus) == 0){
      return "abs";
    }
 //   else if(nProton == 0 && nNeutron == 1 && (nPi0 + nPiPlus + nPiMinus) == 0){
 //     return "ela";
 //   }
    else if(nProton >= 1 && (nPi0 + nPiPlus + nPiMinus) == 0){
      return "pprod";
    }
    else if(nProton == 0 && nNeutron >= 1 && (nPi0 + nPiPlus + nPiMinus) == 0){
      return "inel";
    }
   

    return "";
}

G4NeutronReweighter::~G4NeutronReweighter(){}
