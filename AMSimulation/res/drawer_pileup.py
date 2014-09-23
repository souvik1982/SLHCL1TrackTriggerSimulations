#!/usr/bin/env python

from rootdrawing import *
from roothelper import *
from math import pi

# ______________________________________________________________________________
# Configurations

samples = {}
samples["nu140"        ] = True
samples["mu140"        ] = False
samples["minbias"      ] = False
samples["minbias_remix"] = False

sections = {}
sections["minbias_single"       ] = False
sections["rate_by_module"       ] = True
sections["rate_by_superstrip"   ] = False
sections["nstubs_by_layer"      ] = False
sections["nmodules_by_layer"    ] = False
sections["nsuperstrips_by_layer"] = False
sections["fixme"                ] = False

drawerInit = DrawerInit()
gStyle.SetNumberContours(100)
gStyle.SetPalette(55)  # rainbow color map

# Muon gun
#infiles = ["/eos/uscms/store/user/l1upgrades/SLHC/GEN/620_SLHC12p1_ntuple/SingleMuMinus_20140714/ntuple_1_1_1TX.root"]
#infiles = ["/uscms_data/d2/jiafu/L1TrackTrigger/CRAB_amsim/ntuple_1_1_1TX_redux.root"]
infiles = ["/eos/uscms/store/user/l1upgrades/SLHC/GEN/620_SLHC12p1/SingleMuMinus_20140821/SingleMu_E2023TTI_ntuple_1_1_oGy.root"]

col  = TColor.GetColor("#1f78b4")  # Paired
fcol = TColor.GetColor("#a6cee3")
imgdir = "figures_pileup/"

# Neutrino gun (140PU)
if samples["nu140"]:
    infiles = ["/eos/uscms/store/user/l1upgrades/SLHC/GEN/620_SLHC12p1_ntuple/Neutrino_Pt2to20_gun_20140821/ntuple_1_1_9cK.root", "/eos/uscms/store/user/l1upgrades/SLHC/GEN/620_SLHC12p1_ntuple/Neutrino_Pt2to20_gun_20140821/ntuple_2_1_HJw.root"]
    col  = TColor.GetColor("#e31a1c")  # Paired
    fcol = TColor.GetColor("#fb9a99")
    imgdir = "figures_pileup_nu140/"

# Muon gun (140PU)
if samples["mu140"]:
    infiles = ["/eos/uscms/store/user/l1upgrades/SLHC/GEN/620_SLHC12p1_ntuple/SingleMuMinusFlatPt0p2To150_20140821/ntuple_1_1_dzk.root", "/eos/uscms/store/user/l1upgrades/SLHC/GEN/620_SLHC12p1_ntuple/SingleMuMinusFlatPt0p2To150_20140821/ntuple_2_1_j6Z.root"]
    col  = TColor.GetColor("#6a3d9a")  # Paired
    fcol = TColor.GetColor("#cab2d6")
    imgdir = "figures_pileup_mu140/"

# MinBias
if samples["minbias"]:
    infiles = get_infiles("/uscms_data/d2/jiafu/L1TrackTrigger/CRAB_amsim/input_MinBias_20140821.txt", fast=False)
    col  = TColor.GetColor("#ff7f00")  # Paired
    fcol = TColor.GetColor("#fdbf6f")
    imgdir = "figures_pileup_minbias/"

if samples["minbias_remix"]:
    infiles = ["/uscms_data/d2/jiafu/L1TrackTrigger/CRAB_amsim/Neutrino_E2023TTI_PU140_ntuple.0.root"]
    col  = TColor.GetColor("#ff7f00")  # Paired
    fcol = TColor.GetColor("#fdbf6f")
    imgdir = "figures_pileup_minbias/"


# Number of events
nentries = 1000
#nentries = 20

chain = TChain("ntupler/tree", "")
for f in infiles:
    chain.Add(f)
tree = chain

if not imgdir.endswith("/"):  imgdir += "/"
if gSystem.AccessPathName(imgdir):
    gSystem.mkdir(imgdir)


# ______________________________________________________________________________
# Load

ttmap = json.load(open("../data/trigger_sector_map.json"), object_pairs_hook=convert_key_to_int)
ttrmap = get_reverse_map(ttmap)
eb = EtaBinning("#eta", 60, -3, 3)
pb = EtaBinning("#phi", 64, -3.2, 3.2)


# ______________________________________________________________________________
if sections["minbias_single"]:

    pass

# ______________________________________________________________________________
if sections["rate_by_module"]:

    gStyle.SetLabelSize(0.05, "XY")
    gStyle.SetNdivisions(510, "XY")

    def bookModule():
        histos = {}
        for i in xrange(5,11):  # barrel
            histos["b%i" % i] = TH2F("b%i" % i, "; Barrel module index; Barrel ladder index", b_nmods[i-5], 0, b_nmods[i-5], b_nlads[i-5], 0, b_nlads[i-5])

        for i in xrange(11,23): # endcap
            if i == 16 or i == 17:  continue
            histos["e%i" % i] = TH2F("e%i" % i, "; r: Endcap ring index+%i; #theta: Endcap module index" % e_offset, 2*e_nrings[0], -e_nrings[0], e_nrings[0], 2*e_nrings[0], -e_nrings[0], e_nrings[0])  # a square frame

            for j in xrange(0,15):  # endcap rings
                histos["e%i_r%i" % (i,j)] = TH2F("e%i_r%i" % (i,j), "", e_nmods[j], 0, 2*pi, e_nrings[0], 0, e_nrings[0])

        histos["tt"] = TH2F("tt", "; Trigger tower eta index; Trigger tower phi index", tt_netas, 1, tt_netas+1, tt_nphis, 1, tt_nphis+1)
        return histos

    def projectModule(tree, histos, nentries=1000000000, sim=True):
        tree.SetBranchStatus("*", 0)
        tree.SetBranchStatus("TTStubs_modId"         , 1)

        def fill(moduleId):
            lay = decodeLayer(moduleId)
            lad = decodeLadder(moduleId)
            mod = decodeModule(moduleId)

            if lay < 11:  # barrel
                histos["b%i" % (lay)].Fill(mod, lad, 1)

            else:         # endcap
                rad = 2*pi * (mod+0.5) / e_nmods[lad]
                histos["e%i_r%i" % (lay,lad)].Fill(rad, lad + e_offset, 1)

            if moduleId in ttrmap:
                for tt in ttrmap[moduleId]:
                    tteta = (tt / tt_nphis) + 1
                    ttphi = (tt % tt_nphis) + 1
                    histos["tt"].Fill(tteta, ttphi, 1)
            return

        # Loop over events
        for i_ievt, ievt in enumerate(tree):
            if (i_ievt == nentries):  break

            # Loop over stubs
            for moduleId in ievt.TTStubs_modId:
                fill(moduleId)

        # Divide by number of entries to get average
        for k, v in histos.iteritems():
            v.Scale(1.0/float(i_ievt))

        tree.SetBranchStatus("*", 1)
        return

    def drawModule(histos, imgdir):
        oldTextSize = latex.GetTextSize()
        latex.SetTextSize(0.06)

        # Get zmax
        zmax = 0
        for k, v in histos.iteritems():
            if k.startswith("b") or k.startswith("e"):
                zmax = max(zmax, v.GetMaximum())
        for k, v in histos.iteritems():
            if k.startswith("b") or k.startswith("e"):
                v.SetMinimum(0); v.SetMaximum(zmax)

        # Draw barrel
        for i in xrange(5,11):
            hname = "b%i" % i
            draw2D([histos[hname]], stats=False)
            latex.DrawLatex(0.62, 0.88, "Barrel %i" % (i-4))
            save(imgdir, "rate_by_module_%s" % hname)

        # Draw endcap
        for i in xrange(11,23):
            if i == 16 or i == 17:  continue
            hname = "e%i" % i
            draw2D([histos[hname]], stats=False, palette=False)

            for j in xrange(0,15):
                hname1 = "e%i_r%i" % (i,j)
                if j == 0:
                    histos[hname1].Draw("same pol colz")
                    gPad.Modified(); gPad.Update()
                    movePalette2D(histos[hname1])
                    gPad.Modified(); gPad.Update()
                else:
                    histos[hname1].Draw("same pol col")
            if i < 18:
                latex.DrawLatex(0.62, 0.88, "Endcap +%i" % (i-10))
            else:
                latex.DrawLatex(0.62, 0.88, "Endcap -%i" % (i-17))
            save(imgdir, "rate_by_module_%s" % hname)

        # Draw trigger tower
        hname = "tt"
        histos[hname].SetMinimum(0)
        draw2D([histos[hname]], stats=False)
        save(imgdir, "rate_by_module_%s" % hname)

        latex.SetTextSize(oldTextSize)
        donotdelete = []
        return donotdelete

    def drawModule1D(histos, imgdir, ytitle="stub rate per module"):
        def modifyBarrel(h1):
            xlow, xup = -100, 100
            nbinsx = h1.GetNbinsX()
            h = TH1F(h1.GetName()+"_i", "; %s" % h1.GetXaxis().GetTitle(), nbinsx, xlow, xup)
            for ix in xrange(nbinsx):
                h.SetBinContent(ix+1, h1.GetBinContent(ix+1))
            return h

        def modifyEndcap(h1, side):
            xlow, xup = -20, 20
            nbinsx = h1.GetNbinsX()
            h = TH1F(h1.GetName()+"_i", "; %s" % h1.GetXaxis().GetTitle(), 2 * nbinsx, xlow, xup)
            if side == 1:
                for ix in xrange(nbinsx):
                    h.SetBinContent(nbinsx+ix+1, h1.GetBinContent(ix+1))
            elif side == -1:
                for ix in xrange(nbinsx):
                    h.SetBinContent(nbinsx-ix, h1.GetBinContent(ix+1))
            return h

        def modifyTriggerTower(h1):
            xlow, xup = 0.5, 6.5
            nbinsx = h1.GetNbinsX()
            h = TH1F(h1.GetName()+"_i", "; %s" % h1.GetXaxis().GetTitle(), nbinsx, xlow, xup)
            for ix in xrange(nbinsx):
                h.SetBinContent(ix+1, h1.GetBinContent(ix+1))
            return h

        # Draw barrel
        ymax = 10.0/2 * 1.5
        for i in xrange(5,11):
            hname = "b%i" % i
            hname_px = "b%i_px" % i
            h2 = histos[hname]
            h1 = h2.ProjectionX(hname_px)
            h1.Scale(1.0/h2.GetNbinsY())
            h = modifyBarrel(h1)
            histos[hname_px] = h

            if i-5 == 0:
                h.SetStats(0); h.SetMinimum(0); h.SetMaximum(ymax)
                h.SetTitle("; Barrel module arbitrary unit; %s" % ytitle)
                h.Draw("p")
            h.SetMarkerColor(paletteSet1[i-5]); h.SetLineColor(paletteSet1[i-5]); h.SetMarkerSize(1.3)
            h.Draw("same p")

        moveLegend(0.56,0.70,0.94,0.94); legend.Clear()
        for i in xrange(5,11):
            legend.AddEntry(histos["b%i_px" % i] , "Barrel layer %i" % (i-4), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "rate_by_module_1D_%s" % hname)

        # Draw endcap +
        ymax = 10.0 * 1.5
        for i in xrange(11,16):
            hname = "e%i_r%i" % (i,0)
            hname_py = "e%i_r%i_py" % (i,0)
            h2 = histos[hname]
            h1 = h2.ProjectionY(hname_py)
            h1.Scale(1.0/h2.GetNbinsX())

            for j in xrange(0,15):
                if j == 0:  continue
                hname = "e%i_r%i" % (i,j)
                hname_py = "e%i_r%i_py" % (i,j)
                hh2 = histos[hname]
                hh1 = hh2.ProjectionY(hname_py)
                hh1.Scale(1.0/hh2.GetNbinsX())
                h1.Add(hh1)

            hname = "e%i" % i
            hname_py = "e%i_py" % i
            h = modifyEndcap(h1, 1)
            histos[hname_py] = h

            if i-11 == 0:
                h.SetStats(0); h.SetMinimum(0); h.SetMaximum(ymax)
                h.SetTitle("; Endcap module arbitrary unit; %s" % ytitle)
                h.Draw("p")
            h.SetMarkerColor(paletteSet1[i-11]); h.SetLineColor(paletteSet1[i-11]); h.SetMarkerSize(1.3)
            h.Draw("same p")

        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(11,16):
            legend.AddEntry(histos["e%i_py" % i] , "Endcap disk +%i" % (i-10), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "rate_by_module_1D_%s" % hname)

        # Draw endcap -
        ymax = 10.0 * 1.5
        for i in xrange(18,23):
            hname = "e%i_r%i" % (i,0)
            hname_py = "e%i_r%i_py" % (i,0)
            h2 = histos[hname]
            h1 = h2.ProjectionY(hname_py)
            h1.Scale(1.0/h2.GetNbinsX())

            for j in xrange(0,15):
                if j == 0:  continue
                hname = "e%i_r%i" % (i,j)
                hname_py = "e%i_r%i_py" % (i,j)
                hh2 = histos[hname]
                hh1 = hh2.ProjectionY(hname_py)
                hh1.Scale(1.0/hh2.GetNbinsX())
                h1.Add(hh1)

            hname = "e%i" % i
            hname_py = "e%i_py" % i
            h = modifyEndcap(h1, -1)
            histos[hname_py] = h

            if i-18 == 0:
                h.SetStats(0); h.SetMinimum(0); h.SetMaximum(ymax)
                h.SetTitle("; Endcap module arbitrary unit; %s" % ytitle)
                h.Draw("p")
            h.SetMarkerColor(paletteSet1[i-18]); h.SetLineColor(paletteSet1[i-18]); h.SetMarkerSize(1.3)
            h.Draw("same p")

        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(18,23):
            legend.AddEntry(histos["e%i_py" % i] , "Endcap disk -%i" % (i-17), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "rate_by_module_1D_%s" % hname)

        # Draw trigger tower
        ymax = 400.0 * 1.5
        hname = "tt"
        hname_px = "tt_px"
        h2 = histos[hname]
        h1 = h2.ProjectionX(hname_px)
        h1.Scale(1.0/h2.GetNbinsY())
        h = modifyTriggerTower(h1)
        histos[hname_px] = h

        h.SetStats(0); h.SetMinimum(0); h.SetMaximum(ymax)
        h.SetTitle("; Trigger tower arbitrary unit; stub rate per tower")
        h.SetMarkerColor(paletteSet1[0]); h.SetLineColor(paletteSet1[0]); h.SetMarkerSize(1.3)
        h.Draw("p")
        CMS_label()
        save(imgdir, "rate_by_module_1D_%s" % hname)

        donotdelete = []
        return donotdelete

    histos = bookModule()
    projectModule(tree, histos, nentries=nentries)
    d = drawModule(histos, imgdir)
    d = drawModule1D(histos, imgdir)
    print tree.GetEntries(), histos.items()[0][1].GetEntries()


# ______________________________________________________________________________
if sections["rate_by_superstrip"]:

    gStyle.SetLabelSize(0.05, "XY")
    gStyle.SetNdivisions(510, "XY")

    def bookModule():
        histos = {}
        for i in xrange(5,11):  # barrel
            histos["b%i" % i] = TH1F("b%i" % i, "; Barrel module arbitrary unit", b_nmods[i-5], 0, b_nmods[i-5])

        for i in xrange(11,23): # endcap
            if i == 16 or i == 17:  continue
            histos["e%i" % i] = TH1F("e%i" % i, "; Endcap module arbitrary unit", e_nrings[0], 0, e_nrings[0])

        for i in xrange(1):     # trigger tower
            histos["tt"] = TH1F("tt", "; Trigger tower arbitrary unit", tt_netas, 1, tt_netas+1)
            histos["tt"].Sumw2()
        return histos

    def projectModule(tree, histos, nentries=1000000000, sim=True):
        tree.SetBranchStatus("*", 0)
        tree.SetBranchStatus("TTStubs_modId"         , 1)

        def fill(moduleId):
            lay = decodeLayer(moduleId)
            lad = decodeLadder(moduleId)
            mod = decodeModule(moduleId)

            if isPSModule(moduleId):
                nsssms = 60  # use superstrip-32
            else:
                nsssms = 64  # use superstrip-32

            if lay < 11:    # barrel
                histos["b%i" % (lay)].Fill(mod, 1.0/nsssms)
            else:           # endcap
                histos["e%i" % (lay)].Fill(lad + e_offset, 1.0/nsssms)

            if moduleId in ttrmap:
                for tt in ttrmap[moduleId]:
                    tteta = (tt / tt_nphis) + 1
                    ttphi = (tt % tt_nphis) + 1
                    histos["tt"].Fill(tteta, 1.0/nsssms)
            return

        # Loop over events
        for i_ievt, ievt in enumerate(tree):
            if (i_ievt == nentries):  break

            # Loop over stubs
            for moduleId in ievt.TTStubs_modId:
                fill(moduleId)

        # Divide by number of entries to get average
        for k, v in histos.iteritems():
            v.Scale(1.0/float(i_ievt))

        tree.SetBranchStatus("*", 1)
        return

    def drawModule1D(histos, imgdir, ytitle="stub rate per superstrip"):
        def modifyBarrel(h1):
            xlow, xup = -100, 100
            nbinsx = h1.GetNbinsX()
            h = TH1F(h1.GetName()+"_i", "; %s" % h1.GetXaxis().GetTitle(), nbinsx, xlow, xup)
            for ix in xrange(nbinsx):
                h.SetBinContent(ix+1, h1.GetBinContent(ix+1))
            return h

        def modifyEndcap(h1, side):
            xlow, xup = -20, 20
            nbinsx = h1.GetNbinsX()
            h = TH1F(h1.GetName()+"_i", "; %s" % h1.GetXaxis().GetTitle(), 2 * nbinsx, xlow, xup)
            if side == 1:
                for ix in xrange(nbinsx):
                    h.SetBinContent(nbinsx+ix+1, h1.GetBinContent(ix+1))
            elif side == -1:
                for ix in xrange(nbinsx):
                    h.SetBinContent(nbinsx-ix, h1.GetBinContent(ix+1))
            return h

        def modifyTriggerTower(h1):
            xlow, xup = 0.5, 6.5
            nbinsx = h1.GetNbinsX()
            h = TH1F(h1.GetName()+"_i", "; %s" % h1.GetXaxis().GetTitle(), nbinsx, xlow, xup)
            for ix in xrange(nbinsx):
                h.SetBinContent(ix+1, h1.GetBinContent(ix+1))
            return h

        # Draw barrel
        ymax = 10.0/2/60 * 1.5
        for i in xrange(5,11):
            hname = "b%i" % i
            hname_px = "b%i_px" % i
            h1 = histos[hname]
            h1.Scale(1.0/b_nlads[i-5])
            h = modifyBarrel(h1)
            histos[hname_px] = h

            if i-5 == 0:
                h.SetStats(0); h.SetMinimum(0); h.SetMaximum(ymax)
                h.SetTitle("; Barrel module arbitrary unit; %s" % ytitle)
                h.Draw("p")
            h.SetMarkerColor(paletteSet1[i-5]); h.SetLineColor(paletteSet1[i-5]); h.SetMarkerSize(1.3)
            h.Draw("same p")

        moveLegend(0.56,0.70,0.94,0.94); legend.Clear()
        for i in xrange(5,11):
            legend.AddEntry(histos["b%i_px" % i] , "Barrel layer %i" % (i-4), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "rate_by_superstrip_1D_%s" % hname)

        # Draw endcap +
        ymax = 10.0/60 * 1.5
        for i in xrange(11,16):
            hname = "e%i" % i
            hname_py = "e%i_py" % i
            h1 = histos[hname]
            for j in xrange(0,15):  # scale every ring
                jj = j+e_offset + 1
                h1.SetBinContent(jj, h1.GetBinContent(jj) / e_nmods[j])
            h = modifyEndcap(h1, 1)
            histos[hname_py] = h

            if i-11 == 0:
                h.SetStats(0); h.SetMinimum(0); h.SetMaximum(ymax)
                h.SetTitle("; Endcap module arbitrary unit; %s" % ytitle)
                h.Draw("p")
            h.SetMarkerColor(paletteSet1[i-11]); h.SetLineColor(paletteSet1[i-11]); h.SetMarkerSize(1.3)
            h.Draw("same p")

        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(11,16):
            legend.AddEntry(histos["e%i_py" % i] , "Endcap disk +%i" % (i-10), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "rate_by_superstrip_1D_%s" % hname)

        # Draw endcap -
        ymax = 10.0/60 * 1.5
        for i in xrange(18,23):
            hname = "e%i" % i
            hname_py = "e%i_py" % i
            h1 = histos[hname]
            for j in xrange(0,15):  # scale every ring
                jj = j+e_offset + 1
                h1.SetBinContent(jj, h1.GetBinContent(jj) / e_nmods[j])
            h = modifyEndcap(h1, -1)
            histos[hname_py] = h

            if i-18 == 0:
                h.SetStats(0); h.SetMinimum(0); h.SetMaximum(ymax)
                h.SetTitle("; Endcap module arbitrary unit; %s" % ytitle)
                h.Draw("p")
            h.SetMarkerColor(paletteSet1[i-18]); h.SetLineColor(paletteSet1[i-18]); h.SetMarkerSize(1.3)
            h.Draw("same p")

        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(18,23):
            legend.AddEntry(histos["e%i_py" % i] , "Endcap disk -%i" % (i-17), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "rate_by_superstrip_1D_%s" % hname)

        donotdelete = []
        return donotdelete

    histos = bookModule()
    projectModule(tree, histos, nentries=nentries)
    d = drawModule1D(histos, imgdir)
    print tree.GetEntries(), histos.items()[0][1].GetEntries()


# ______________________________________________________________________________
if sections["nstubs_by_layer"]:

    gStyle.SetTitleSize(0.04, "Y")
    gStyle.SetTitleOffset(1.3, "Y")

    def bookLayer():
        histos = {}
        histos2 = {}
        fillings = {}

        for j in xrange(4):
            for i in xrange(1):
                if True:    # all
                    hname = "a%i_mc%i" % (i,j)
                histos[hname] = TProfile(hname, "; %s; <# stubs> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # stubs_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx

            for i in xrange(5,23):
                if i == 16 or i == 17:  continue
                if i < 11:  # barrel
                    hname = "b%i_mc%i" % (i,j)
                else:       # endcap
                    hname = "e%i_mc%i" % (i,j)
                histos[hname] = TProfile(hname, "; %s; <# stubs> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # stubs_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx

            for i in xrange(48):
                if True:    # trigger tower
                    hname = "tt%i_mc%i" % (i,j)
                histos[hname] = TProfile(hname, "; %s; <# stubs> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # stubs_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx
        return (histos, histos2, fillings)

    def projectLayer(tree, histos, histos2, fillings, nentries=1000000000, sim=True):
        tree.SetBranchStatus("*", 0)
        tree.SetBranchStatus("TTStubs_eta"           , 1)
        tree.SetBranchStatus("TTStubs_phi"           , 1)
        tree.SetBranchStatus("TTStubs_isGenuine"     , 1)
        tree.SetBranchStatus("TTStubs_isCombinatoric", 1)
        tree.SetBranchStatus("TTStubs_isUnknown"     , 1)
        tree.SetBranchStatus("TTStubs_modId"         , 1)

        def fill(moduleId, mc, eta):
            lay = decodeLayer(moduleId)
            ix = eb.findBin(eta)

            hname  = "a%i_mc%i" % (0,mc)
            fillings[hname][ix] += 1

            if lay < 11:  # barrel
                hname  = "b%i_mc%i" % (lay,mc)
            else:         # endcap
                hname  = "e%i_mc%i" % (lay,mc)
            fillings[hname][ix] += 1

            if moduleId in ttrmap:
                for tt in ttrmap[moduleId]:
                    hname  = "tt%i_mc%i" % (tt,mc)
                    fillings[hname][ix] += 1

        def fill_histo():
            for j in xrange(4):
                for i in xrange(1):
                    if True:    # all
                        hname = "a%i_mc%i" % (i,j)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

                for i in xrange(5,23):
                    if i == 16 or i == 17:  continue
                    if i < 11:  # barrel
                        hname = "b%i_mc%i" % (i,j)
                    else:       # endcap
                        hname = "e%i_mc%i" % (i,j)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

                for i in xrange(48):
                    if True:    # trigger tower
                        hname = "tt%i_mc%i" % (i,j)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

        # Loop over events
        for i_ievt, ievt in enumerate(tree):
            if (i_ievt == nentries):  break

            # Loop over stubs (1)
            TTStubs_mc = []
            for genuine, combina, unknown in izip(ievt.TTStubs_isGenuine, ievt.TTStubs_isCombinatoric, ievt.TTStubs_isUnknown):
                mc = 1 * genuine + 2 * combina + 3 * unknown
                assert(mc == 3)
                TTStubs_mc.append(mc)

            # Loop over stubs (2)
            for mc, eta, phi, moduleId in izip(TTStubs_mc, ievt.TTStubs_eta, ievt.TTStubs_phi, ievt.TTStubs_modId):
                fill(moduleId, 0, eta)
                fill(moduleId, mc, eta)
            fill_histo()

        tree.SetBranchStatus("*", 0)
        return

    def drawLayer(histos, histos2, ymaxscales, ymaxscales2, hnlambda, imgdir):
        # Get ymax
        assert(len(ymaxscales) == len(ymaxscales2) and len(ymaxscales) == 4)  # combined, barrel, endcap, tt
        hname = "a%i" % 0
        ymax = histos[hnlambda(hname)].GetMaximum()
        ymax2 = histos2[hnlambda(hname)].GetMaximum()


        # Draw combined
        i = 0
        hname = "a%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[0]))
        h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
        h.Draw()
        CMS_label()
        save(imgdir, "nstubs_by_layer_%s" % hnlambda(hname))

        i = 0
        hname = "a%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[0]))
        h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
        h.Draw("p")
        CMS_label()
        save(imgdir, "nstubs_by_layer_max_%s" % hnlambda(hname))

        # Draw barrel
        i = 5
        hname = "b%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[1]))
        h.Draw()
        for i in xrange(5,11):
            hname1 = "b%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-5]); h.SetLineColor(paletteSet1[i-5]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.70,0.94,0.94); legend.Clear()
        for i in xrange(5,11):
            hname1 = "b%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Barrel layer %i" % (i-4), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nstubs_by_layer_%s" % hnlambda(hname))

        i = 5
        hname = "b%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[1]))
        h.Draw("p")
        for i in xrange(5,11):
            hname1 = "b%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-5]); h.SetLineColor(paletteSet1[i-5]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nstubs_by_layer_max_%s" % hnlambda(hname))

        # Draw endcap +
        i = 11
        hname = "e%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[2]))
        h.Draw()
        for i in xrange(11,16):
            hname1 = "e%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-11]); h.SetLineColor(paletteSet1[i-11]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(11,16):
            hname1 = "e%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Endcap disk +%i" % (i-10), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nstubs_by_layer_%s" % hnlambda(hname))

        i = 11
        hname = "e%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[2]))
        h.Draw("p")
        for i in xrange(11,16):
            hname1 = "e%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-11]); h.SetLineColor(paletteSet1[i-11]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nstubs_by_layer_max_%s" % hnlambda(hname))

        # Draw endcap -
        i = 18
        hname = "e%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[2]))
        h.Draw()
        for i in xrange(18,23):
            hname1 = "e%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-18]); h.SetLineColor(paletteSet1[i-18]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(18,23):
            hname1 = "e%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Endcap disk -%i" % (i-17), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nstubs_by_layer_%s" % hnlambda(hname))

        i = 18
        hname = "e%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[2]))
        h.Draw("p")
        for i in xrange(18,23):
            hname1 = "e%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-18]); h.SetLineColor(paletteSet1[i-18]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nstubs_by_layer_max_%s" % hnlambda(hname))

        # Draw trigger tower
        for iphi in xrange(8):
            i = 0
            tt = i*8 + iphi
            hname = "tt%i" % tt
            h = histos[hnlambda(hname)]
            h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[3]))
            h.Draw()
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                h = histos[hnlambda(hname1)]
                h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
                h.Draw("same")
            moveLegend(0.56,0.70,0.94,0.94); legend.Clear()
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                legend.AddEntry(histos[hnlambda(hname1)], "Trigger tower %i" % tt, "p")
            legend.Draw()
            CMS_label()
            save(imgdir, "nstubs_by_layer_%s" % hnlambda(hname))

            i = 0
            tt = i*8 + iphi
            hname = "tt%i" % tt
            h = histos2[hnlambda(hname)]
            h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[3]))
            h.Draw("p")
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                h = histos2[hnlambda(hname1)]
                h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
                h.Draw("same p")
            legend.Draw()
            CMS_label()
            save(imgdir, "nstubs_by_layer_max_%s" % hnlambda(hname))

        donotdelete = []
        return donotdelete

    histos, histos2, fillings = bookLayer()
    projectLayer(tree, histos, histos2, fillings, nentries=nentries)
    ymaxscales  = [1.5, 1.5/2, 1.5/2, 1.5/4]
    ymaxscales2 = ymaxscales
    d = drawLayer(histos, histos2, ymaxscales, ymaxscales2, lambda x: x+"_mc0", imgdir)
    print tree.GetEntries(), histos.items()[0][1].GetEntries()


# ______________________________________________________________________________
if sections["nmodules_by_layer"]:

    gStyle.SetTitleSize(0.04, "Y")
    gStyle.SetTitleOffset(1.3, "Y")
    coordmap = json.load(open("../data/module_coordinates.json"), object_pairs_hook=convert_key_to_int)

    def bookLayer():
        histos = {}
        histos2 = {}
        fillings = {}

        for j in xrange(4):
            for i in xrange(1):
                if True:    # all
                    hname = "a%i_mc%i" % (i,j)
                histos[hname] = TProfile(hname, "; %s; <# modules> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # modules_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx
                histos["oc_"+hname] = TProfile("oc_"+hname, "; %s; <module occupancy> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2["oc_"+hname] = TH1F("oc_"+hname+"_i", "; %s; module occupancy_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)

            for i in xrange(5,23):
                if i == 16 or i == 17:  continue
                if i < 11:  # barrel
                    hname = "b%i_mc%i" % (i,j)
                else:       # endcap
                    hname = "e%i_mc%i" % (i,j)
                histos[hname] = TProfile(hname, "; %s; <# modules> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # modules_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx
                histos["oc_"+hname] = TProfile("oc_"+hname, "; %s; <module occupancy> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2["oc_"+hname] = TH1F("oc_"+hname+"_i", "; %s; module occupancy_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)

            for i in xrange(48):
                if True:    # trigger tower
                    hname = "tt%i_mc%i" % (i,j)
                histos[hname] = TProfile(hname, "; %s; <# modules> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # modules_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx
                histos["oc_"+hname] = TProfile("oc_"+hname, "; %s; <module occupancy> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2["oc_"+hname] = TH1F("oc_"+hname+"_i", "; %s; module occupancy_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
        return (histos, histos2, fillings)

    def projectLayer(tree, histos, histos2, fillings, nentries=1000000000, sim=True):
        tree.SetBranchStatus("*", 0)
        tree.SetBranchStatus("TTStubs_isGenuine"     , 1)
        tree.SetBranchStatus("TTStubs_isCombinatoric", 1)
        tree.SetBranchStatus("TTStubs_isUnknown"     , 1)
        tree.SetBranchStatus("TTStubs_modId"         , 1)

        def fill(moduleId, mc, eta):
            lay = decodeLayer(moduleId)
            ix = eb.findBin(eta)

            hname  = "a%i_mc%i" % (0,mc)
            fillings[hname][ix] += 1

            if lay < 11:  # barrel
                hname  = "b%i_mc%i" % (lay,mc)
            else:         # endcap
                hname  = "e%i_mc%i" % (lay,mc)
            fillings[hname][ix] += 1

            if moduleId in ttrmap:
                for tt in ttrmap[moduleId]:
                    hname  = "tt%i_mc%i" % (tt,mc)
                    fillings[hname][ix] += 1

        def fill_histo():
            for j in xrange(4):
                for i in xrange(1):
                    if True:    # all
                        hname = "a%i_mc%i" % (i,j)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

                for i in xrange(5,23):
                    if i == 16 or i == 17:  continue
                    if i < 11:  # barrel
                        hname = "b%i_mc%i" % (i,j)
                    else:       # endcap
                        hname = "e%i_mc%i" % (i,j)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

                for i in xrange(48):
                    if True:    # trigger tower
                        hname = "tt%i_mc%i" % (i,j)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

        def oc_fill(moduleId, mc, n, eta):
            lay = decodeLayer(moduleId)
            ix = eb.findBin(eta)

            hname  = "a%i_mc%i" % (0,mc)
            h, hh = histos["oc_"+hname], histos2["oc_"+hname]
            h.Fill(eb.getBinCenter(ix), n)
            hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), n))

            if lay < 11:  # barrel
                hname  = "b%i_mc%i" % (lay,mc)
            else:         # endcap
                hname  = "e%i_mc%i" % (lay,mc)
            h, hh = histos["oc_"+hname], histos2["oc_"+hname]
            h.Fill(eb.getBinCenter(ix), n)
            hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), n))

            if moduleId in ttrmap:
                for tt in ttrmap[moduleId]:
                    hname  = "tt%i_mc%i" % (tt,mc)
                    h, hh = histos["oc_"+hname], histos2["oc_"+hname]
                    h.Fill(eb.getBinCenter(ix), n)
                    hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), n))

        # Loop over events
        for i_ievt, ievt in enumerate(tree):
            if (i_ievt == nentries):  break

            # Loop over stubs (1)
            TTStubs_mc = []
            for genuine, combina, unknown in izip(ievt.TTStubs_isGenuine, ievt.TTStubs_isCombinatoric, ievt.TTStubs_isUnknown):
                mc = 1 * genuine + 2 * combina + 3 * unknown
                assert(mc == 3)
                TTStubs_mc.append(mc)

            results = {}

            # Loop over stubs (2)
            for mc, moduleId in izip(TTStubs_mc, ievt.TTStubs_modId):
                if moduleId not in results:
                    results[moduleId] = [0] * 4  # init
                results[moduleId][0] += 1
                results[moduleId][mc] += 1

            # Loop over found moduleId
            for moduleId, mc_n_4 in results.iteritems():
                eta = coordmap[moduleId][2]
                for mc, n in enumerate(mc_n_4):
                    if n > 0:
                        fill(moduleId, mc, eta)
            fill_histo()

            # Loop over all moduleId
            for moduleId, coord in coordmap.iteritems():
                eta = coord[2]
                if moduleId not in results:
                    mc_n_4 = [0] * 4
                else:
                    mc_n_4 = results[moduleId]

                for j in xrange(4):
                    oc_fill(moduleId, j, mc_n_4[j], eta)

        tree.SetBranchStatus("*", 0)
        return

    def drawLayer(histos, histos2, ymaxscales, ymaxscales2, hnlambda, imgdir):
        # Get ymax
        assert(len(ymaxscales) == len(ymaxscales2) and len(ymaxscales) == 4)  # combined, barrel, endcap, tt
        hname = "a%i" % 0
        ymax = histos[hnlambda(hname)].GetMaximum()
        ymax2 = histos2[hnlambda(hname)].GetMaximum()


        # Draw combined
        i = 0
        hname = "a%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[0]))
        h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
        h.Draw()
        CMS_label()
        save(imgdir, "nmodules_by_layer_%s" % hnlambda(hname))

        i = 0
        hname = "a%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[0]))
        h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
        h.Draw("p")
        CMS_label()
        save(imgdir, "nmodules_by_layer_max_%s" % hnlambda(hname))

        # Draw barrel
        i = 5
        hname = "b%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[1]))
        h.Draw()
        for i in xrange(5,11):
            hname1 = "b%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-5]); h.SetLineColor(paletteSet1[i-5]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.70,0.94,0.94); legend.Clear()
        for i in xrange(5,11):
            hname1 = "b%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Barrel layer %i" % (i-4), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nmodules_by_layer_%s" % hnlambda(hname))

        i = 5
        hname = "b%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[1]))
        h.Draw("p")
        for i in xrange(5,11):
            hname1 = "b%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-5]); h.SetLineColor(paletteSet1[i-5]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nmodules_by_layer_max_%s" % hnlambda(hname))

        # Draw endcap +
        i = 11
        hname = "e%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[2]))
        h.Draw()
        for i in xrange(11,16):
            hname1 = "e%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-11]); h.SetLineColor(paletteSet1[i-11]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(11,16):
            hname1 = "e%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Endcap disk +%i" % (i-10), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nmodules_by_layer_%s" % hnlambda(hname))

        i = 11
        hname = "e%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[2]))
        h.Draw("p")
        for i in xrange(11,16):
            hname1 = "e%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-11]); h.SetLineColor(paletteSet1[i-11]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nmodules_by_layer_max_%s" % hnlambda(hname))

        # Draw endcap -
        i = 18
        hname = "e%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[2]))
        h.Draw()
        for i in xrange(18,23):
            hname1 = "e%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-18]); h.SetLineColor(paletteSet1[i-18]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(18,23):
            hname1 = "e%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Endcap disk -%i" % (i-17), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nmodules_by_layer_%s" % hnlambda(hname))

        i = 18
        hname = "e%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[2]))
        h.Draw("p")
        for i in xrange(18,23):
            hname1 = "e%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-18]); h.SetLineColor(paletteSet1[i-18]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nmodules_by_layer_max_%s" % hnlambda(hname))

        # Draw trigger tower
        for iphi in xrange(8):
            i = 0
            tt = i*8 + iphi
            hname = "tt%i" % tt
            h = histos[hnlambda(hname)]
            h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[3]))
            h.Draw()
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                h = histos[hnlambda(hname1)]
                h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
                h.Draw("same")
            moveLegend(0.56,0.70,0.94,0.94); legend.Clear()
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                legend.AddEntry(histos[hnlambda(hname1)], "Trigger tower %i" % tt, "p")
            legend.Draw()
            CMS_label()
            save(imgdir, "nmodules_by_layer_%s" % hnlambda(hname))

            i = 0
            tt = i*8 + iphi
            hname = "tt%i" % tt
            h = histos2[hnlambda(hname)]
            h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[3]))
            h.Draw("p")
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                h = histos2[hnlambda(hname1)]
                h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
                h.Draw("same p")
            legend.Draw()
            CMS_label()
            save(imgdir, "nmodules_by_layer_max_%s" % hnlambda(hname))

        donotdelete = []
        return donotdelete

    histos, histos2, fillings = bookLayer()
    projectLayer(tree, histos, histos2, fillings, nentries=nentries)
    ymaxscales  = [1.5, 1.5/2, 1.5/2, 1.5/4]
    ymaxscales2 = ymaxscales
    d = drawLayer(histos, histos2, ymaxscales, ymaxscales2, lambda x: x+"_mc0", imgdir)
    ymaxscales  = [1.5, 1.5/2, 1.5, 1.5/2]
    ymaxscales2 = [1.5, 1.5, 1.5, 1.5]
    d = drawLayer(histos, histos2, ymaxscales, ymaxscales2, lambda x: "oc_"+x+"_mc0", imgdir)
    print tree.GetEntries(), histos.items()[0][1].GetEntries()


# ______________________________________________________________________________
if sections["nsuperstrips_by_layer"]:

    gStyle.SetTitleSize(0.04, "Y")
    gStyle.SetTitleOffset(1.3, "Y")
    coordmap = json.load(open("../data/module_coordinates.json"), object_pairs_hook=convert_key_to_int)

    def encode_sssm(moduleId, col, row):
        """Small superstrip size: ss32"""

        if isPSModule(moduleId):
            col >>= 4
        row >>= 5
        s = (moduleId << 11) | (col << 10) | row
        return s

    def encode_sslg(moduleId, col, row):
        """Large superstrip size: ss256"""

        if isPSModule(moduleId):
            col >>= 4
        row >>= 8
        s = (moduleId << 11) | (col << 10) | row
        return s

    def decode_moduleId(ssId):
        m = ssId >> 11
        return m

    def bookLayer():
        histos = {}
        histos2 = {}
        fillings = {}

        for hvar in ["nsssms", "nsslgs"]:
            for i in xrange(1):
                if True:    # all
                    hname = "%s_a%i" % (hvar,i)
                histos[hname] = TProfile(hname, "; %s; <# superstrips> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # superstrips_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx
                histos["oc_"+hname] = TProfile("oc_"+hname, "; %s; <superstrip occupancy> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2["oc_"+hname] = TH1F("oc_"+hname+"_i", "; %s; superstrip occupancy_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)

            for i in xrange(5,23):
                if i == 16 or i == 17:  continue
                if i < 11:  # barrel
                    hname = "%s_b%i" % (hvar,i)
                else:       # endcap
                    hname = "%s_e%i" % (hvar,i)
                histos[hname] = TProfile(hname, "; %s; <# superstrips> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # superstrips_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx
                histos["oc_"+hname] = TProfile("oc_"+hname, "; %s; <superstrip occupancy> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2["oc_"+hname] = TH1F("oc_"+hname+"_i", "; %s; superstrip occupancy_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)

            for i in xrange(48):
                if True:    # trigger tower
                    hname = "%s_tt%i" % (hvar,i)
                histos[hname] = TProfile(hname, "; %s; <# superstrips> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2[hname] = TH1F(hname+"_i", "; %s; # superstrips_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
                fillings[hname] = [0] * eb.nbinsx
                histos["oc_"+hname] = TProfile("oc_"+hname, "; %s; <superstrip occupancy> per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup, 0, 100000)
                histos2["oc_"+hname] = TH1F("oc_"+hname+"_i", "; %s; superstrip occupancy_{max} per #eta unit of 0.1" % eb.xtitle, eb.nbinsx, eb.xlow, eb.xup)
        return (histos, histos2, fillings)

    def projectLayer(tree, histos, histos2, fillings, nentries=1000000000, sim=True):
        tree.SetBranchStatus("*", 0)
        tree.SetBranchStatus("TTStubs_modId"         , 1)
        tree.SetBranchStatus("TTStubs_coordx"        , 1)
        tree.SetBranchStatus("TTStubs_coordy"        , 1)

        def fill(moduleId, hvar, eta):
            lay = decodeLayer(moduleId)
            ix = eb.findBin(eta)

            hname  = "%s_a%i" % (hvar,0)
            fillings[hname][ix] += 1

            if lay < 11:  # barrel
                hname  = "%s_b%i" % (hvar,lay)
            else:         # endcap
                hname  = "%s_e%i" % (hvar,lay)
            fillings[hname][ix] += 1

            if moduleId in ttrmap:
                for tt in ttrmap[moduleId]:
                    hname  = "%s_tt%i" % (hvar,tt)
                    fillings[hname][ix] += 1

        def fill_histo():
            for hvar in ["nsssms", "nsslgs"]:
                for i in xrange(1):
                    if True:    # all
                        hname  = "%s_a%i" % (hvar,i)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

                for i in xrange(5,23):
                    if i == 16 or i == 17:  continue
                    if i < 11:  # barrel
                        hname  = "%s_b%i" % (hvar,i)
                    else:       # endcap
                        hname  = "%s_e%i" % (hvar,i)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

                for i in xrange(48):
                    if True:    # trigger tower
                        hname = "%s_tt%i" % (hvar,i)
                    h, hh, f = histos[hname], histos2[hname], fillings[hname]
                    for ix in xrange(eb.nbinsx):
                        h.Fill(eb.getBinCenter(ix), f[ix])
                        hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), f[ix]))
                        f[ix] = 0  # rezero

        def oc_fill(moduleId, hvar, n, eta):
            lay = decodeLayer(moduleId)
            ix = eb.findBin(eta)

            hname  = "%s_a%i" % (hvar,0)
            h, hh = histos["oc_"+hname], histos2["oc_"+hname]
            h.Fill(eb.getBinCenter(ix), n)
            hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), n))

            if lay < 11:  # barrel
                hname  = "%s_b%i" % (hvar,lay)
            else:         # endcap
                hname  = "%s_e%i" % (hvar,lay)
            h, hh = histos["oc_"+hname], histos2["oc_"+hname]
            h.Fill(eb.getBinCenter(ix), n)
            hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), n))

            if moduleId in ttrmap:
                for tt in ttrmap[moduleId]:
                    hname  = "%s_tt%i" % (hvar,tt)
                    h, hh = histos["oc_"+hname], histos2["oc_"+hname]
                    h.Fill(eb.getBinCenter(ix), n)
                    hh.SetBinContent(ix+1, max(hh.GetBinContent(ix+1), n))

        # Generate all superstrips
        moduleId_sssm = {}
        moduleId_sslg = {}
        for moduleId, coord in coordmap.iteritems():
            for col in xrange(2):
                if isPSModule(moduleId):
                    col <<= 4
                    row_max = 960
                else:
                    row_max = 1016
                sssm_min = encode_sssm(moduleId, col, 0)
                sssm_max = encode_sssm(moduleId, col, row_max-1)
                for sssm in xrange(sssm_min, sssm_max+1):
                    moduleId_sssm.setdefault(moduleId,[]).append(sssm)

                sslg_min = encode_sslg(moduleId, col, 0)
                sslg_max = encode_sslg(moduleId, col, row_max-1)
                for sslg in xrange(sslg_min, sslg_max+1):
                    moduleId_sslg.setdefault(moduleId,[]).append(sslg)

        # Loop over events
        for i_ievt, ievt in enumerate(tree):
            if (i_ievt == nentries):  break

            results_sssm = {}
            results_sslg = {}

            # Loop over stubs
            for moduleId, coordx, coordy in izip(ievt.TTStubs_modId, ievt.TTStubs_coordx, ievt.TTStubs_coordy):
                col = halfStripRound(coordy)
                row = halfStripRound(coordx)
                col >>= 1
                row >>= 1

                sssm = encode_sssm(moduleId, col, row)
                sslg = encode_sslg(moduleId, col, row)
                results_sssm[sssm] = results_sssm.get(sssm, 0) + 1
                results_sslg[sslg] = results_sslg.get(sslg, 0) + 1

            # Loop over found superstrips
            for sssm, n in results_sssm.iteritems():
                moduleId = decode_moduleId(sssm)
                eta = coordmap[moduleId][2]
                if n > 0:
                    fill(moduleId, "nsssms", eta)
            for sslg, n in results_sslg.iteritems():
                moduleId = decode_moduleId(sslg)
                eta = coordmap[moduleId][2]
                if n > 0:
                    fill(moduleId, "nsslgs", eta)
            fill_histo()

            # Loop over all superstrips
            for moduleId, coord in coordmap.iteritems():
                eta = coord[2]
                for sssm in moduleId_sssm[moduleId]:
                    n = results_sssm.get(sssm, 0)
                    oc_fill(moduleId, "nsssms", n, eta)
                for sslg in moduleId_sslg[moduleId]:
                    n = results_sslg.get(sslg, 0)
                    oc_fill(moduleId, "nsslgs", n, eta)

        tree.SetBranchStatus("*", 0)
        return

    def drawLayer(histos, histos2, ymaxscales, ymaxscales2, hnlambda, imgdir):
        # Get ymax
        assert(len(ymaxscales) == len(ymaxscales2) and len(ymaxscales) == 4)  # combined, barrel, endcap, tt
        hname = "a%i" % 0
        ymax = histos[hnlambda(hname)].GetMaximum()
        ymax2 = histos2[hnlambda(hname)].GetMaximum()


        # Draw combined
        i = 0
        hname = "a%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[0]))
        h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
        h.Draw()
        CMS_label()
        save(imgdir, "nsuperstrips_by_layer_%s" % hnlambda(hname))

        i = 0
        hname = "a%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[0]))
        h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
        h.Draw("p")
        CMS_label()
        save(imgdir, "nsuperstrips_by_layer_max_%s" % hnlambda(hname))

        # Draw barrel
        i = 5
        hname = "b%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[1]))
        h.Draw()
        for i in xrange(5,11):
            hname1 = "b%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-5]); h.SetLineColor(paletteSet1[i-5]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.70,0.94,0.94); legend.Clear()
        for i in xrange(5,11):
            hname1 = "b%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Barrel layer %i" % (i-4), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nsuperstrips_by_layer_%s" % hnlambda(hname))

        i = 5
        hname = "b%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[1]))
        h.Draw("p")
        for i in xrange(5,11):
            hname1 = "b%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-5]); h.SetLineColor(paletteSet1[i-5]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nsuperstrips_by_layer_max_%s" % hnlambda(hname))

        # Draw endcap +
        i = 11
        hname = "e%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[2]))
        h.Draw()
        for i in xrange(11,16):
            hname1 = "e%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-11]); h.SetLineColor(paletteSet1[i-11]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(11,16):
            hname1 = "e%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Endcap disk +%i" % (i-10), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nsuperstrips_by_layer_%s" % hnlambda(hname))

        i = 11
        hname = "e%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[2]))
        h.Draw("p")
        for i in xrange(11,16):
            hname1 = "e%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-11]); h.SetLineColor(paletteSet1[i-11]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nsuperstrips_by_layer_max_%s" % hnlambda(hname))

        # Draw endcap -
        i = 18
        hname = "e%i" % i
        h = histos[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[2]))
        h.Draw()
        for i in xrange(18,23):
            hname1 = "e%i" % i
            h = histos[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-18]); h.SetLineColor(paletteSet1[i-18]); h.SetMarkerSize(1.3)
            h.Draw("same")
        moveLegend(0.56,0.74,0.94,0.94); legend.Clear()
        for i in xrange(18,23):
            hname1 = "e%i" % i
            legend.AddEntry(histos[hnlambda(hname1)], "Endcap disk -%i" % (i-17), "p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nsuperstrips_by_layer_%s" % hnlambda(hname))

        i = 18
        hname = "e%i" % i
        h = histos2[hnlambda(hname)]
        h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[2]))
        h.Draw("p")
        for i in xrange(18,23):
            hname1 = "e%i" % i
            h = histos2[hnlambda(hname1)]
            h.SetMarkerColor(paletteSet1[i-18]); h.SetLineColor(paletteSet1[i-18]); h.SetMarkerSize(1.3)
            h.Draw("same p")
        legend.Draw()
        CMS_label()
        save(imgdir, "nsuperstrips_by_layer_max_%s" % hnlambda(hname))

        # Draw trigger tower
        for iphi in xrange(8):
            i = 0
            tt = i*8 + iphi
            hname = "tt%i" % tt
            h = histos[hnlambda(hname)]
            h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax * ymaxscales[3]))
            h.Draw()
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                h = histos[hnlambda(hname1)]
                h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
                h.Draw("same")
            moveLegend(0.56,0.70,0.94,0.94); legend.Clear()
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                legend.AddEntry(histos[hnlambda(hname1)], "Trigger tower %i" % tt, "p")
            legend.Draw()
            CMS_label()
            save(imgdir, "nsuperstrips_by_layer_%s" % hnlambda(hname))

            i = 0
            tt = i*8 + iphi
            hname = "tt%i" % tt
            h = histos2[hnlambda(hname)]
            h.SetStats(0); h.SetMinimum(0); h.SetMaximum((ymax2 * ymaxscales2[3]))
            h.Draw("p")
            for i in xrange(6):
                tt = i*8 + iphi
                hname1 = "tt%i" % tt
                h = histos2[hnlambda(hname1)]
                h.SetMarkerColor(paletteSet1[i]); h.SetLineColor(paletteSet1[i]); h.SetMarkerSize(1.3)
                h.Draw("same p")
            legend.Draw()
            CMS_label()
            save(imgdir, "nsuperstrips_by_layer_max_%s" % hnlambda(hname))

        donotdelete = []
        return donotdelete

    histos, histos2, fillings = bookLayer()
    projectLayer(tree, histos, histos2, fillings, nentries=nentries/5)  # too slow!
    ymaxscales  = [1.5, 1.5/2, 1.5/2, 1.5/4]
    ymaxscales2 = ymaxscales
    d = drawLayer(histos, histos2, ymaxscales, ymaxscales2, lambda x: "nsssms_"+x, imgdir)
    d = drawLayer(histos, histos2, ymaxscales, ymaxscales2, lambda x: "nsslgs_"+x, imgdir)
    ymaxscales  = [1.5, 1.5/2, 1.5, 1.5/2]
    ymaxscales2 = [1.5, 1.5, 1.5, 1.5]
    d = drawLayer(histos, histos2, ymaxscales, ymaxscales2, lambda x: "oc_nsssms_"+x, imgdir)
    d = drawLayer(histos, histos2, ymaxscales, ymaxscales2, lambda x: "oc_nsslgs_"+x, imgdir)
    print tree.GetEntries(), histos.items()[0][1].GetEntries()


# ______________________________________________________________________________
if sections["fixme"]:

    pass