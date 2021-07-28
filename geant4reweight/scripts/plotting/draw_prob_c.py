from ROOT import * 
import sys
from os import listdir as ls
from draw_utils import * 
from argparse import ArgumentParser 
from ROOT import * 
from math import log, sqrt

def getChi2(w, v):
  result = []  
  chi2 = 0.
  nbins = 0
  for i in range(1,w.GetNbinsX()+1):
    if(  (w.GetBinError(i) == 0) and (v.GetBinError(i) == 0) ) :
      continue
    
    a = ( (w.GetBinContent(i) - v.GetBinContent(i))**2 ) / ( w.GetBinError(i)**2 + v.GetBinError(i)**2  ) 
    chi2 = chi2 + a 
    nbins = nbins + 1
  result.append(chi2)
  print nbins
  result.append(nbins)
  return result

def init_parser():
  parser = ArgumentParser()
  parser.add_argument('-i', type=str, help='Inelastic variation factor', default="1")
  parser.add_argument('-e', type=str, help='Elastic variation factor', default="1")
  parser.add_argument('--loc', type=str, help='Location of samples')
  parser.add_argument('--nom', type=str, help='nom File name')
  parser.add_argument('--var', type=str, help='var File name')
  parser.add_argument('--cmd', type=str, help='Which command to execute ', default=" ")
  parser.add_argument('-f', type=str, help='Which input file')
  parser.add_argument('--plot',type=str, help='Plot name')
  return parser

def SetStyle(h):
  h.SetTitle("Pi+ Ar - Thin Target Scattering")
  h.SetXTitle("KE (MeV)")
  h.SetYTitle("#sigma (barn)")
  h.GetXaxis().SetTitleSize(.05)
  h.GetYaxis().SetTitleSize(.05)
  h.GetYaxis().SetTitleOffset(.8)
  h.GetXaxis().SetTitleOffset(.8)

gStyle.SetLabelFont(62,"XYZ")
gStyle.SetTitleFont(62,"XYZ")
 
args = init_parser().parse_args()
inel = args.i
elast = args.e
loc = args.loc
cmd = args.cmd
plot = args.plot
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

names = ["surv", "elast", "abs", "cex", "dcex", "prod", "inel"] 

titles = {"surv":"No Interaction",
          "elast":"Elastic Scatters",
          "abs":"Pion Absorption",
          "cex":"Single Charge Exchange",
          "dcex":"Double Charge Exchange",
          "prod":"Pion Production",
          "inel":"Inelastic"}

if (cmd == "Draw" or cmd == "draw"):
  inFile = TFile(loc + "/" + args.f, "UPDATE") 

  for name in names:
    c = TCanvas(name, name)
    nhist = inFile.Get("n"+name) 
    nhist.SetFillColor(0)
    whist = inFile.Get("w"+name) 
    vhist = inFile.Get("v"+name) 
    whist.SetFillColor(0)
    vhist.SetFillColor(0)

    nhist.SetTitle(titles[name])
    vhist.SetTitle(titles[name])
    whist.SetTitle(titles[name])

    nhist.SetXTitle("Pion Momentum (MeV)")
    vhist.SetXTitle("Pion Momentum (MeV)")
    whist.SetXTitle("Pion Momentum (MeV)")

    nhist.SetYTitle("Fraction")
    vhist.SetYTitle("Fraction")
    whist.SetYTitle("Fraction")

    nhist.SetMarkerStyle(20) 
    whist.SetMarkerStyle(21)
    vhist.SetMarkerStyle(22)
    nhist.SetMarkerColor(4) 
    whist.SetMarkerColor(2)
    vhist.SetMarkerColor(1)
    
    leg = TLegend(.55,.7,.9,.9)
    leg.AddEntry(nhist, "Nominal", "lp")
    leg.AddEntry(whist, "Weighted", "lp")
    leg.AddEntry(vhist, "Varied", "lp")
   

    whist.SetLineColor(2)
    vhist.SetLineColor(1)

    vhist.SetMaximum(.6)
    vhist.SetMinimum(0.)
    vhist.Draw("pE hist")
    whist.Draw("pE same hist")
    nhist.Draw("pE same")
    leg.Draw("same")

    c.Write()
    c.SaveAs(name+"_"+plot)



elif (cmd == "ratio" or cmd == "Ratio"):
  inFile = TFile(loc + "/" + args.f, "READ") 
  for name in names:
    w = inFile.Get("w"+name)  
    v = inFile.Get("v"+name)  

    r = w.Clone()

    r.Divide(v)  

    r.SetMinimum(0.)
    r.SetMaximum(2.0)

    c1 = TCanvas()
    r.SetTitle(titles[name])
    r.Draw("p")

    f = TF1("line", "1", 0, 1200.)
    f.SetLineColor(1)
    f.Draw("same")

    c1.SaveAs(name+"_ratio_"+plot)

else:

  #units: mb
  #scale =1.E27/ (.5 * 2.266 * 6.022E23 / 12.01 )
  scale = 1.

  surv_cut = "(int != \"pi+Inelastic\" && nElast == 0)"
  abs_cut =  "(int == \"pi+Inelastic\" && (nPi0 + nPiPlus + nPiMinus) == 0)"
  inel_cut = "(int == \"pi+Inelastic\" && (nPi0 + nPiMinus) == 0 && (nPiPlus == 1))"
  cex_cut =  "(int == \"pi+Inelastic\" && (nPiPlus + nPiMinus) == 0 && (nPi0 == 1))"
  dcex_cut = "(int == \"pi+Inelastic\" && (nPiPlus + nPi0) == 0 && (nPiMinus == 1))"
  prod_cut = "(int == \"pi+Inelastic\" && (nPiPlus + nPi0 + nPiMinus) > 1)"
  elast_cut = "(int != \"pi+Inelastic\" && nElast > 0)"


  cuts = {"surv":surv_cut,
    "abs":abs_cut,
    "inel":inel_cut,
    "cex":cex_cut,
    "dcex":dcex_cut,
    "prod":prod_cut,
    "elast":elast_cut
  }


  nhists = dict()
  whists = dict()
  vhists = dict()


  colors = {"surv":kRed,
             "abs":kYellow,
            "inel":kBlue,
             "cex":kGreen,
            "dcex":kGray,
            "prod":kBlack,
           "elast":kPink
  }

  outfile = TFile(loc+"/"+args.f,"RECREATE")
  
  fileName = loc + "/" + args.nom 
  nomFile = TFile(fileName,"READ")
  nomTree = nomFile.Get("tree")
  
  fileName = loc + "/" + args.var
  varFile = TFile(fileName,"READ")
  varTree = varFile.Get("tree")
  
  nIncident = nomTree.GetEntries()
  
  outfile.cd()
  
  nStack = THStack("nStack", "")
  wStack = THStack("wStack", "")
  vStack = THStack("vStack", "")

  nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>nTotal(100,200,300)","","goff")
  nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>wTotal(100,200,300)","weight*elastWeight","goff")
  varTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>vTotal(100,200,300)","","goff")

  nTotal = gDirectory.Get("nTotal")
  wTotal = gDirectory.Get("wTotal")
  vTotal = gDirectory.Get("vTotal")

  nTotal.Sumw2() 
  wTotal.Sumw2() 
  vTotal.Sumw2() 

  nTotal.Write() 
  wTotal.Write() 
  vTotal.Write() 

  for name in names:
    cut = cuts[name]
    print name, cut
    nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>n"+name+"(100,200,300)", cut,"goff")
    nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>w"+name+"(100,200,300)","weight*elastWeight*" + cut,"goff")
    varTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>v"+name+"(100,200,300)", cut,"goff")
  
    nhists[name] = gDirectory.Get("n"+name) 
    nhists[name].Sumw2()
    nhists[name].Divide(nTotal)
    nhists[name].SetFillColor(colors[name])
    nStack.Add(nhists[name])

    whists[name] = gDirectory.Get("w"+name) 
    whists[name].SetFillColor(colors[name])
    whists[name].Sumw2()
    whists[name].Divide(wTotal)
    wStack.Add(whists[name])

    vhists[name] = gDirectory.Get("v"+name) 
    vhists[name].SetFillColor(colors[name])
    vhists[name].Sumw2()
    vhists[name].Divide(vTotal)
    vStack.Add(vhists[name])

    nhists[name].Scale(scale) 
    whists[name].Scale(scale)  
    vhists[name].Scale(scale)  

    print nhists[name].Integral()
    nhists[name].Write() 
    whists[name].Write()  
    vhists[name].Write()  


  nStack.Write()
  wStack.Write()
  vStack.Write()
  outfile.Close()


