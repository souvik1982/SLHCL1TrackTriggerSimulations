#ifndef NTupleTools_NTupleGenJets_h_
#define NTupleTools_NTupleGenJets_h_

#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"

namespace reco { class GenJet; }

class NTupleGenJets : public edm::EDProducer {
  public:
    explicit NTupleGenJets(const edm::ParameterSet&);

  private:
    //virtual void beginJob();
    virtual void produce(edm::Event&, const edm::EventSetup&);
    //virtual void endJob();

    const edm::InputTag inputTag_;
    const std::string   prefix_, suffix_;

    StringCutObjectSelector<reco::GenJet> selector_;
    const unsigned int  maxN_;
};

#endif