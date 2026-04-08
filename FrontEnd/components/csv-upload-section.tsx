"use client"

import type React from "react"

import { useState } from "react"
import { Upload, FileSpreadsheet, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export function CsvUploadSection() {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith(".csv")) {
      setFile(droppedFile)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  return (
    <section id="upload" className="py-20 bg-gradient-to-b from-[#E7F2EF] to-white relative overflow-hidden">
      <div className="absolute top-0 right-0 w-96 h-96 bg-[#A1C2BD] rounded-full blur-[150px] opacity-20"></div>
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-[#708993] rounded-full blur-[120px] opacity-15"></div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-3xl mx-auto text-center space-y-4 mb-12">
          <h2 className="text-4xl font-bold text-[#19183B]">Upload Your Product Data</h2>
          <p className="text-lg text-[#708993]">
            Upload a CSV file containing your product sales data to get started with AI-powered insights
          </p>
        </div>

        <Card className="max-w-2xl mx-auto p-8 shadow-xl hover:shadow-2xl transition-all border-2 border-[#A1C2BD]/30 bg-white/80 backdrop-blur-sm">
          <div
            onDrop={handleDrop}
            onDragOver={(e) => {
              e.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => setIsDragging(false)}
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
              isDragging
                ? "border-[#A1C2BD] bg-[#A1C2BD]/10 scale-105 shadow-lg shadow-[#A1C2BD]/30"
                : "border-[#708993]/40 hover:border-[#A1C2BD] hover:bg-[#E7F2EF]/50"
            }`}
          >
            {file ? (
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-gradient-to-br from-[#A1C2BD] to-[#708993] rounded-full flex items-center justify-center shadow-lg">
                  <CheckCircle2 className="w-8 h-8 text-white" />
                </div>
                <div>
                  <p className="font-semibold text-lg text-[#19183B]">{file.name}</p>
                  <p className="text-sm text-[#708993]">{(file.size / 1024).toFixed(2)} KB</p>
                </div>
                <Button
                  onClick={() => setFile(null)}
                  variant="outline"
                  className="mt-4 border-[#708993] text-[#708993] hover:bg-[#708993] hover:text-white"
                >
                  Remove File
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-gradient-to-br from-[#A1C2BD] to-[#708993] rounded-full flex items-center justify-center shadow-lg">
                  <Upload className="w-8 h-8 text-white" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-[#19183B] mb-2">Drag and drop your CSV file here</p>
                  <p className="text-sm text-[#708993] mb-4">or</p>
                  <label htmlFor="file-upload">
                    <Button
                      asChild
                      className="bg-[#A1C2BD] hover:bg-[#8fb3ae] text-[#19183B] shadow-lg shadow-[#A1C2BD]/30"
                    >
                      <span className="cursor-pointer">Browse Files</span>
                    </Button>
                  </label>
                  <input id="file-upload" type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
                </div>
                <div className="flex items-center justify-center gap-2 text-sm text-[#708993]">
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Accepts .csv files only</span>
                </div>
              </div>
            )}
          </div>

          {file && (
            <div className="mt-6">
              <Button
                className="w-full bg-gradient-to-r from-[#A1C2BD] to-[#708993] hover:from-[#8fb3ae] hover:to-[#5f7580] text-white shadow-lg"
                size="lg"
              >
                Analyze Data
              </Button>
            </div>
          )}
        </Card>
      </div>
    </section>
  )
}
