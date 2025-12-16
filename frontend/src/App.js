import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Calculator } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { toast, Toaster } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [countries, setCountries] = useState([]);
  const [calculations, setCalculations] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    user_name: "",
    project_name: "",
    country: "",
    fence_type: "",
    meters: "",
    gates: ""
  });
  
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchCountries();
    fetchCalculations();
  }, []);

  const fetchCountries = async () => {
    try {
      const response = await axios.get(`${API}/countries`);
      setCountries(response.data.countries);
    } catch (error) {
      console.error("Error fetching countries:", error);
      toast.error("Failed to load countries");
    }
  };

  const fetchCalculations = async () => {
    try {
      const response = await axios.get(`${API}/calculations`);
      setCalculations(response.data);
    } catch (error) {
      console.error("Error fetching calculations:", error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCalculate = async () => {
    if (!formData.user_name || !formData.project_name || !formData.country || 
        !formData.fence_type || !formData.meters || !formData.gates) {
      toast.error("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/calculate`, {
        user_name: formData.user_name,
        project_name: formData.project_name,
        country: formData.country,
        fence_type: formData.fence_type,
        meters: parseFloat(formData.meters),
        gates: parseInt(formData.gates)
      });
      
      setResult(response.data.calculation);
      fetchCalculations();
      toast.success("Calculation completed!");
    } catch (error) {
      console.error("Error calculating:", error);
      toast.error("Failed to calculate price");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      user_name: "",
      project_name: "",
      country: "",
      fence_type: "",
      meters: "",
      gates: ""
    });
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Toaster position="top-right" />
      
      <header className="bg-[#2D4A2B] border-b-2 border-[#234520]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="bg-white px-3 py-2 rounded-sm">
              <img 
                src="https://customer-assets.emergentagent.com/job_meter-price-tool/artifacts/a3m47d7y_NEW%20LOGO.png" 
                alt="Duralock Logo" 
                className="h-10 sm:h-12 w-auto"
              />
            </div>
            <div>
              <h1 className="font-heading text-2xl sm:text-3xl font-black text-white tracking-tight">
                Duracost - Installation
              </h1>
              <p className="text-slate-200 text-sm mt-1">Calculate installation costs per meter</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          <div data-testid="input-panel" className="space-y-6">
            <Card className="rounded-sm border-2 border-slate-300 bg-white shadow-sm p-6">
              <h2 className="font-heading text-xl font-bold text-slate-900 mb-6 tracking-tight">
                Project Details
              </h2>
              
              <div className="space-y-5">
                <div>
                  <Label htmlFor="user_name" className="text-sm font-medium text-slate-700 mb-2 block">
                    Your Name
                  </Label>
                  <Input
                    id="user_name"
                    data-testid="user-name-input"
                    placeholder="Enter your name"
                    value={formData.user_name}
                    onChange={(e) => handleInputChange("user_name", e.target.value)}
                    className="rounded-sm border-2 border-slate-300 focus:border-amber-500 focus:ring-0 bg-white"
                  />
                </div>

                <div>
                  <Label htmlFor="project_name" className="text-sm font-medium text-slate-700 mb-2 block">
                    Project Name
                  </Label>
                  <Input
                    id="project_name"
                    data-testid="project-name-input"
                    placeholder="Enter project name"
                    value={formData.project_name}
                    onChange={(e) => handleInputChange("project_name", e.target.value)}
                    className="rounded-sm border-2 border-slate-300 focus:border-amber-500 focus:ring-0 bg-white"
                  />
                </div>

                <div>
                  <Label htmlFor="country" className="text-sm font-medium text-slate-700 mb-2 block">
                    Country
                  </Label>
                  <Select value={formData.country} onValueChange={(value) => handleInputChange("country", value)}>
                    <SelectTrigger data-testid="country-select" className="rounded-sm border-2 border-slate-300 focus:border-amber-500 focus:ring-0 bg-white">
                      <SelectValue placeholder="Select country" />
                    </SelectTrigger>
                    <SelectContent>
                      {countries.map((country) => (
                        <SelectItem key={country} value={country}>{country}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="fence_type" className="text-sm font-medium text-slate-700 mb-2 block">
                    Fence Type
                  </Label>
                  <Select value={formData.fence_type} onValueChange={(value) => handleInputChange("fence_type", value)}>
                    <SelectTrigger data-testid="fence-type-select" className="rounded-sm border-2 border-slate-300 focus:border-amber-500 focus:ring-0 bg-white">
                      <SelectValue placeholder="Select fence type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="OR">OR - Oval Running Rail (136m/day)</SelectItem>
                      <SelectItem value="PR">PR - Post and Rail (128m/day)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="meters" className="text-sm font-medium text-slate-700 mb-2 block">
                    Total Meters
                  </Label>
                  <Input
                    id="meters"
                    data-testid="meters-input"
                    type="number"
                    placeholder="Enter total meters"
                    value={formData.meters}
                    onChange={(e) => handleInputChange("meters", e.target.value)}
                    className="rounded-sm border-2 border-slate-300 focus:border-amber-500 focus:ring-0 bg-white"
                  />
                </div>

                <div>
                  <Label htmlFor="gates" className="text-sm font-medium text-slate-700 mb-2 block">
                    Number of Gates
                  </Label>
                  <Input
                    id="gates"
                    data-testid="gates-input"
                    type="number"
                    placeholder="Enter number of gates"
                    value={formData.gates}
                    onChange={(e) => handleInputChange("gates", e.target.value)}
                    className="rounded-sm border-2 border-slate-300 focus:border-amber-500 focus:ring-0 bg-white"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  data-testid="calculate-button"
                  onClick={handleCalculate}
                  disabled={loading}
                  className="flex-1 rounded-sm border-2 border-slate-900 bg-slate-900 text-white hover:bg-slate-800 shadow-none hover:shadow-[2px_2px_0px_0px_rgba(15,23,42,1)] transition-all duration-150 font-medium"
                >
                  {loading ? "Calculating..." : "Calculate Price"}
                </Button>
                <Button
                  data-testid="reset-button"
                  onClick={handleReset}
                  variant="outline"
                  className="rounded-sm border-2 border-slate-300 hover:bg-slate-100 shadow-none transition-all duration-150"
                >
                  Reset
                </Button>
              </div>
            </Card>
          </div>

          <div data-testid="result-panel" className="space-y-6">
            {result ? (
              <Card className="rounded-sm border-2 border-slate-300 bg-white shadow-sm p-6 grid-pattern relative overflow-hidden">
                <div className="absolute inset-0 bg-white/90 z-0"></div>
                <div className="relative z-10">
                  <h2 className="font-heading text-xl font-bold text-slate-900 mb-4 tracking-tight">
                    Cost Breakdown
                  </h2>
                  
                  <div className="space-y-3 mb-6">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Project:</span>
                      <span className="font-medium text-slate-900">{result.project_name}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Country:</span>
                      <span className="font-medium text-slate-900">{result.country}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Fence Type:</span>
                      <span className="font-medium text-slate-900">{result.fence_type}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Meters:</span>
                      <span className="font-mono font-medium text-slate-900">{result.meters}m</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Gates:</span>
                      <span className="font-mono font-medium text-slate-900">{result.gates}</span>
                    </div>
                  </div>

                  <Separator className="my-4" />

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Work Days:</span>
                      <span className="font-mono font-medium text-slate-900">{result.breakdown.work_days} days</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Labour Cost:</span>
                      <span className="font-mono font-medium text-slate-900">£{result.breakdown.labor_cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Tools Cost:</span>
                      <span className="font-mono font-medium text-slate-900">£{result.breakdown.tools_cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Supervision:</span>
                      <span className="font-mono font-medium text-slate-900">£{result.breakdown.supervision_cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Flight Ticket:</span>
                      <span className="font-mono font-medium text-slate-900">£{result.breakdown.flight_ticket.toFixed(2)}</span>
                    </div>
                  </div>

                  <Separator className="my-4" />

                  <div className="bg-slate-100 rounded-sm p-4 mb-6">
                    <div className="flex justify-between items-center">
                      <span className="font-heading text-lg font-bold text-slate-900">Raw Total:</span>
                      <span data-testid="raw-total" className="font-mono text-2xl font-bold text-slate-900">£{result.breakdown.raw_total.toFixed(2)}</span>
                    </div>
                  </div>

                  <h3 className="font-heading text-lg font-bold text-slate-900 mb-3 tracking-tight">
                    Markup Options
                  </h3>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between items-center bg-amber-50 border-2 border-amber-200 rounded-sm p-3">
                      <span className="text-sm font-medium text-slate-900">+30% Markup:</span>
                      <span data-testid="markup-30" className="font-mono font-bold text-amber-700">£{result.breakdown.markup_30.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center bg-amber-50 border-2 border-amber-200 rounded-sm p-3">
                      <span className="text-sm font-medium text-slate-900">+40% Markup:</span>
                      <span data-testid="markup-40" className="font-mono font-bold text-amber-700">£{result.breakdown.markup_40.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center bg-amber-50 border-2 border-amber-200 rounded-sm p-3">
                      <span className="text-sm font-medium text-slate-900">+50% Markup:</span>
                      <span data-testid="markup-50" className="font-mono font-bold text-amber-700">£{result.breakdown.markup_50.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center bg-emerald-50 border-2 border-emerald-200 rounded-sm p-3">
                      <span className="text-sm font-medium text-slate-900">+60% Markup:</span>
                      <span data-testid="markup-60" className="font-mono font-bold text-emerald-700">£{result.breakdown.markup_60.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              </Card>
            ) : (
              <Card className="rounded-sm border-2 border-slate-300 bg-white shadow-sm p-12 text-center">
                <Calculator className="w-16 h-16 mx-auto text-slate-300 mb-4" />
                <h3 className="font-heading text-lg font-bold text-slate-900 mb-2">
                  Ready to Calculate
                </h3>
                <p className="text-sm text-slate-600">
                  Fill in the project details and click Calculate to see the pricing breakdown
                </p>
              </Card>
            )}
          </div>
        </div>

        <div data-testid="archive-section" className="mt-12">
          <h2 className="font-heading text-2xl font-bold text-slate-900 mb-6 tracking-tight">
            Calculation Archive
          </h2>
          
          <Card className="rounded-sm border-2 border-slate-300 bg-white shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-900 border-b-2 border-slate-800">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-bold text-white uppercase tracking-wide">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-white uppercase tracking-wide">Project</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-white uppercase tracking-wide">Country</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-white uppercase tracking-wide">Type</th>
                    <th className="px-4 py-3 text-right text-xs font-bold text-white uppercase tracking-wide">Meters</th>
                    <th className="px-4 py-3 text-right text-xs font-bold text-white uppercase tracking-wide">Gates</th>
                    <th className="px-4 py-3 text-right text-xs font-bold text-white uppercase tracking-wide">Raw Total</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-white uppercase tracking-wide">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {calculations.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="px-4 py-8 text-center text-sm text-slate-500">
                        No calculations yet. Create your first one above!
                      </td>
                    </tr>
                  ) : (
                    calculations.map((calc) => (
                      <tr key={calc.id} data-testid="archive-row" className="hover:bg-slate-50 transition-colors duration-150">
                        <td className="px-4 py-3 text-sm text-slate-900 font-medium">{calc.user_name}</td>
                        <td className="px-4 py-3 text-sm text-slate-900">{calc.project_name}</td>
                        <td className="px-4 py-3 text-sm text-slate-700">{calc.country}</td>
                        <td className="px-4 py-3 text-sm font-mono text-slate-700">{calc.fence_type}</td>
                        <td className="px-4 py-3 text-sm font-mono text-right text-slate-700">{calc.meters}m</td>
                        <td className="px-4 py-3 text-sm font-mono text-right text-slate-700">{calc.gates}</td>
                        <td className="px-4 py-3 text-sm font-mono text-right font-medium text-slate-900">£{calc.breakdown.raw_total.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm text-slate-600">{new Date(calc.timestamp).toLocaleDateString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;