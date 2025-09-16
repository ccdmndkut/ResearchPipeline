This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where comments have been removed, empty lines have been removed, content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: client/**, server/**, shared/**, package.json, tsconfig*.json, vite.config.*, drizzle.config.*
- Files matching these patterns are excluded: node_modules/**, dist/**, build/**, .next/**, coverage/**, tests/**, *.log, *.lock, *.env, .DS_Store
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Code comments have been removed from supported file types
- Empty lines have been removed from all files
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
client/index.html
client/src/App.tsx
client/src/components/export-options.tsx
client/src/components/file-upload.tsx
client/src/components/model-evaluation.tsx
client/src/components/persona-analysis.tsx
client/src/components/pipeline-progress.tsx
client/src/components/recommendation.tsx
client/src/components/sidebar.tsx
client/src/components/ui/accordion.tsx
client/src/components/ui/alert-dialog.tsx
client/src/components/ui/alert.tsx
client/src/components/ui/aspect-ratio.tsx
client/src/components/ui/avatar.tsx
client/src/components/ui/badge.tsx
client/src/components/ui/breadcrumb.tsx
client/src/components/ui/button.tsx
client/src/components/ui/calendar.tsx
client/src/components/ui/card.tsx
client/src/components/ui/carousel.tsx
client/src/components/ui/chart.tsx
client/src/components/ui/checkbox.tsx
client/src/components/ui/collapsible.tsx
client/src/components/ui/command.tsx
client/src/components/ui/context-menu.tsx
client/src/components/ui/dialog.tsx
client/src/components/ui/drawer.tsx
client/src/components/ui/dropdown-menu.tsx
client/src/components/ui/form.tsx
client/src/components/ui/hover-card.tsx
client/src/components/ui/input-otp.tsx
client/src/components/ui/input.tsx
client/src/components/ui/label.tsx
client/src/components/ui/menubar.tsx
client/src/components/ui/navigation-menu.tsx
client/src/components/ui/pagination.tsx
client/src/components/ui/popover.tsx
client/src/components/ui/progress.tsx
client/src/components/ui/radio-group.tsx
client/src/components/ui/resizable.tsx
client/src/components/ui/scroll-area.tsx
client/src/components/ui/select.tsx
client/src/components/ui/separator.tsx
client/src/components/ui/sheet.tsx
client/src/components/ui/sidebar.tsx
client/src/components/ui/skeleton.tsx
client/src/components/ui/slider.tsx
client/src/components/ui/switch.tsx
client/src/components/ui/table.tsx
client/src/components/ui/tabs.tsx
client/src/components/ui/textarea.tsx
client/src/components/ui/toast.tsx
client/src/components/ui/toaster.tsx
client/src/components/ui/toggle-group.tsx
client/src/components/ui/toggle.tsx
client/src/components/ui/tooltip.tsx
client/src/hooks/use-mobile.tsx
client/src/hooks/use-toast.ts
client/src/index.css
client/src/lib/queryClient.ts
client/src/lib/utils.ts
client/src/main.tsx
client/src/pages/home.tsx
client/src/pages/not-found.tsx
drizzle.config.ts
package.json
server/index.ts
server/routes.ts
server/services/openai.ts
server/services/pipeline.ts
server/storage.ts
server/vite.ts
shared/schema.ts
tsconfig.json
vite.config.ts
```

# Files

## File: client/index.html
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Architects+Daughter&family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Fira+Code:wght@300..700&family=Geist+Mono:wght@100..900&family=Geist:wght@100..900&family=IBM+Plex+Mono:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500;1,600;1,700&family=IBM+Plex+Sans:ital,wght@0,100..700;1,100..700&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Lora:ital,wght@0,400..700;1,400..700&family=Merriweather:ital,opsz,wght@0,18..144,300..900;1,18..144,300..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Outfit:wght@100..900&family=Oxanium:wght@200..800&family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Mono:ital,wght@0,100..700;1,100..700&family=Roboto:ital,wght@0,100..900;1,100..900&family=Source+Code+Pro:ital,wght@0,200..900;1,200..900&family=Source+Serif+4:ital,opsz,wght@0,8..60,200..900;1,8..60,200..900&family=Space+Grotesk:wght@300..700&family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## File: client/src/App.tsx
```typescript
import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Home from "@/pages/home";
import NotFound from "@/pages/not-found";
function Router()
```

## File: client/src/components/export-options.tsx
```typescript
import { Download, FileText, BarChart3, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
interface ExportOptionsProps {
  pipelineId?: string;
  canExport?: boolean;
  onDownloadPrompt?: () => void;
  onDownloadReport?: () => void;
  onDeploy?: () => void;
}
⋮----
const handleDownloadPrompt = async () =>
const handleDownloadReport = async () =>
```

## File: client/src/components/file-upload.tsx
```typescript
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { CloudUpload, FileText, X, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
interface FileUploadProps {
  onFileUpload: (file: File) => void;
  uploadedFile?: { name: string; size: number };
  onRemoveFile?: () => void;
  isUploading?: boolean;
}
⋮----
const formatFileSize = (bytes: number) =>
```

## File: client/src/components/model-evaluation.tsx
```typescript
import { RefreshCw, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type { EvaluationResult } from "@shared/schema";
interface ModelEvaluationProps {
  results?: EvaluationResult[];
  isEvaluating?: boolean;
  progress?: number;
  onRefresh?: () => void;
}
⋮----
const getStatusBadge = (result: EvaluationResult) =>
```

## File: client/src/components/persona-analysis.tsx
```typescript
import { Download, Volume2, Palette, Star, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { PersonaAnalysis } from "@shared/schema";
interface PersonaAnalysisProps {
  analysis?: PersonaAnalysis;
  systemPrompt?: string;
  isComplete?: boolean;
  onDownload?: () => void;
}
```

## File: client/src/components/pipeline-progress.tsx
```typescript
import { cn } from "@/lib/utils";
import { Upload, Brain, ServerCog, BarChart3 } from "lucide-react";
interface PipelineProgressProps {
  currentStep: 'upload' | 'analyze' | 'evaluate' | 'complete';
  progress?: number;
}
⋮----
const getStepStatus = (stepId: string) =>
⋮----
<div key=
```

## File: client/src/components/recommendation.tsx
```typescript
import { Trophy } from "lucide-react";
import type { EvaluationResult } from "@shared/schema";
interface RecommendationProps {
  bestModel?: string;
  bestResult?: EvaluationResult;
  judgeComments?: string;
}
export function RecommendationCard(
```

## File: client/src/components/sidebar.tsx
```typescript
import { cn } from "@/lib/utils";
import { Bot, Upload, Brain, ServerCog, BarChart3, Download, Play, HelpCircle, Settings } from "lucide-react";
interface SidebarProps {
  currentPipeline?: any;
  onRunPipeline?: () => void;
}
```

## File: client/src/components/ui/accordion.tsx
```typescript
import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/alert-dialog.tsx
```typescript
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"
```

## File: client/src/components/ui/alert.tsx
```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/aspect-ratio.tsx
```typescript

```

## File: client/src/components/ui/avatar.tsx
```typescript
import { cn } from "@/lib/utils"
```

## File: client/src/components/ui/badge.tsx
```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
⋮----
export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}
⋮----
<div className=
```

## File: client/src/components/ui/breadcrumb.tsx
```typescript
import { Slot } from "@radix-ui/react-slot"
import { ChevronRight, MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/button.tsx
```typescript
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
⋮----
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}
```

## File: client/src/components/ui/calendar.tsx
```typescript
import { ChevronLeft, ChevronRight } from "lucide-react"
import { DayPicker } from "react-day-picker"
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"
export type CalendarProps = React.ComponentProps<typeof DayPicker>
```

## File: client/src/components/ui/card.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
⋮----
<div ref=
```

## File: client/src/components/ui/carousel.tsx
```typescript
import useEmblaCarousel, {
  type UseEmblaCarouselType,
} from "embla-carousel-react"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
type CarouselApi = UseEmblaCarouselType[1]
type UseCarouselParameters = Parameters<typeof useEmblaCarousel>
type CarouselOptions = UseCarouselParameters[0]
type CarouselPlugin = UseCarouselParameters[1]
type CarouselProps = {
  opts?: CarouselOptions
  plugins?: CarouselPlugin
  orientation?: "horizontal" | "vertical"
  setApi?: (api: CarouselApi) => void
}
type CarouselContextProps = {
  carouselRef: ReturnType<typeof useEmblaCarousel>[0]
  api: ReturnType<typeof useEmblaCarousel>[1]
  scrollPrev: () => void
  scrollNext: () => void
  canScrollPrev: boolean
  canScrollNext: boolean
} & CarouselProps
⋮----
function useCarousel()
```

## File: client/src/components/ui/chart.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
export type ChartConfig = {
  [k in string]: {
    label?: React.ReactNode
    icon?: React.ComponentType
  } & (
    | { color?: string; theme?: never }
    | { color?: never; theme: Record<keyof typeof THEMES, string> }
  )
}
type ChartContextProps = {
  config: ChartConfig
}
⋮----
function useChart()
⋮----
className=
⋮----
<div className=
```

## File: client/src/components/ui/checkbox.tsx
```typescript
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/collapsible.tsx
```typescript

```

## File: client/src/components/ui/command.tsx
```typescript
import { type DialogProps } from "@radix-ui/react-dialog"
import { Command as CommandPrimitive } from "cmdk"
import { Search } from "lucide-react"
import { cn } from "@/lib/utils"
import { Dialog, DialogContent } from "@/components/ui/dialog"
⋮----
className=
```

## File: client/src/components/ui/context-menu.tsx
```typescript
import { Check, ChevronRight, Circle } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/dialog.tsx
```typescript
import { X } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/drawer.tsx
```typescript
import { Drawer as DrawerPrimitive } from "vaul"
import { cn } from "@/lib/utils"
const Drawer = (
⋮----
className=
```

## File: client/src/components/ui/dropdown-menu.tsx
```typescript
import { Check, ChevronRight, Circle } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/form.tsx
```typescript
import { Slot } from "@radix-ui/react-slot"
import {
  Controller,
  FormProvider,
  useFormContext,
  type ControllerProps,
  type FieldPath,
  type FieldValues,
} from "react-hook-form"
import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"
⋮----
type FormFieldContextValue<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
> = {
  name: TName
}
⋮----
const FormField = <
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
>({
  ...props
}: ControllerProps<TFieldValues, TName>) =>
const useFormField = () =>
type FormItemContextValue = {
  id: string
}
⋮----
<div ref=
⋮----
className=
```

## File: client/src/components/ui/hover-card.tsx
```typescript
import { cn } from "@/lib/utils"
```

## File: client/src/components/ui/input-otp.tsx
```typescript
import { OTPInput, OTPInputContext } from "input-otp"
import { Dot } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
containerClassName=
className=
⋮----
<div ref=
```

## File: client/src/components/ui/input.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/label.tsx
```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
```

## File: client/src/components/ui/menubar.tsx
```typescript
import { Check, ChevronRight, Circle } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/navigation-menu.tsx
```typescript
import { cva } from "class-variance-authority"
import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/pagination.tsx
```typescript
import { ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"
import { ButtonProps, buttonVariants } from "@/components/ui/button"
const Pagination = (
⋮----
className=
⋮----
<li ref=
⋮----
const PaginationPrevious = (
```

## File: client/src/components/ui/popover.tsx
```typescript
import { cn } from "@/lib/utils"
```

## File: client/src/components/ui/progress.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/radio-group.tsx
```typescript
import { Circle } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/resizable.tsx
```typescript
import { GripVertical } from "lucide-react"
⋮----
import { cn } from "@/lib/utils"
```

## File: client/src/components/ui/scroll-area.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/select.tsx
```typescript
import { Check, ChevronDown, ChevronUp } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/separator.tsx
```typescript
import { cn } from "@/lib/utils"
```

## File: client/src/components/ui/sheet.tsx
```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
interface SheetContentProps
  extends React.ComponentPropsWithoutRef<typeof SheetPrimitive.Content>,
    VariantProps<typeof sheetVariants> {}
⋮----
className=
```

## File: client/src/components/ui/sidebar.tsx
```typescript
import { Slot } from "@radix-ui/react-slot"
import { VariantProps, cva } from "class-variance-authority"
import { PanelLeft } from "lucide-react"
import { useIsMobile } from "@/hooks/use-mobile"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
⋮----
type SidebarContextProps = {
  state: "expanded" | "collapsed"
  open: boolean
  setOpen: (open: boolean) => void
  openMobile: boolean
  setOpenMobile: (open: boolean) => void
  isMobile: boolean
  toggleSidebar: () => void
}
⋮----
function useSidebar()
⋮----
const handleKeyDown = (event: KeyboardEvent) =>
⋮----
className=
⋮----
{/* This is what handles the sidebar gap on desktop */}
⋮----
onClick?.(event)
toggleSidebar()
```

## File: client/src/components/ui/skeleton.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/slider.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/switch.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/table.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
⋮----
<thead ref=
```

## File: client/src/components/ui/tabs.tsx
```typescript
import { cn } from "@/lib/utils"
```

## File: client/src/components/ui/textarea.tsx
```typescript
import { cn } from "@/lib/utils"
⋮----
className=
```

## File: client/src/components/ui/toast.tsx
```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"
⋮----
className=
⋮----
type ToastProps = React.ComponentPropsWithoutRef<typeof Toast>
type ToastActionElement = React.ReactElement<typeof ToastAction>
```

## File: client/src/components/ui/toaster.tsx
```typescript
import { useToast } from "@/hooks/use-toast"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast"
```

## File: client/src/components/ui/toggle-group.tsx
```typescript
import { type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { toggleVariants } from "@/components/ui/toggle"
⋮----
className=
```

## File: client/src/components/ui/toggle.tsx
```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
```

## File: client/src/components/ui/tooltip.tsx
```typescript
import { cn } from "@/lib/utils"
```

## File: client/src/hooks/use-mobile.tsx
```typescript
export function useIsMobile()
⋮----
const onChange = () =>
```

## File: client/src/hooks/use-toast.ts
```typescript
import type {
  ToastActionElement,
  ToastProps,
} from "@/components/ui/toast"
⋮----
type ToasterToast = ToastProps & {
  id: string
  title?: React.ReactNode
  description?: React.ReactNode
  action?: ToastActionElement
}
⋮----
function genId()
type ActionType = typeof actionTypes
type Action =
  | {
      type: ActionType["ADD_TOAST"]
      toast: ToasterToast
    }
  | {
      type: ActionType["UPDATE_TOAST"]
      toast: Partial<ToasterToast>
    }
  | {
      type: ActionType["DISMISS_TOAST"]
      toastId?: ToasterToast["id"]
    }
  | {
      type: ActionType["REMOVE_TOAST"]
      toastId?: ToasterToast["id"]
    }
interface State {
  toasts: ToasterToast[]
}
⋮----
const addToRemoveQueue = (toastId: string) =>
export const reducer = (state: State, action: Action): State =>
⋮----
function dispatch(action: Action)
type Toast = Omit<ToasterToast, "id">
function toast(
⋮----
const update = (props: ToasterToast)
const dismiss = () => dispatch(
⋮----
function useToast()
```

## File: client/src/index.css
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
:root {
.dark {
@layer base {
⋮----
* {
⋮----
@apply border-border;
⋮----
body {
⋮----
.upload-zone {
.upload-zone:hover,
.step-indicator {
.step-indicator::after {
.step-indicator:last-child::after {
.step-indicator.completed .step-circle {
.step-indicator.active .step-circle {
.code-block {
```

## File: client/src/lib/queryClient.ts
```typescript
import { QueryClient, QueryFunction } from "@tanstack/react-query";
async function throwIfResNotOk(res: Response)
export async function apiRequest(
  method: string,
  url: string,
  data?: unknown | undefined,
): Promise<Response>
type UnauthorizedBehavior = "returnNull" | "throw";
export const getQueryFn: <T>(options: {
  on401: UnauthorizedBehavior;
}) => QueryFunction<T> =
(
```

## File: client/src/lib/utils.ts
```typescript
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
export function cn(...inputs: ClassValue[])
```

## File: client/src/main.tsx
```typescript
import { createRoot } from "react-dom/client";
import App from "./App";
```

## File: client/src/pages/home.tsx
```typescript
import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { apiRequest } from "@/lib/queryClient";
import { Sidebar } from "@/components/sidebar";
import { FileUpload } from "@/components/file-upload";
import { PipelineProgress } from "@/components/pipeline-progress";
import { PersonaAnalysisResults } from "@/components/persona-analysis";
import { ModelEvaluationResults } from "@/components/model-evaluation";
import { RecommendationCard } from "@/components/recommendation";
import { ExportOptions } from "@/components/export-options";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { HelpCircle, Settings } from "lucide-react";
import type { Pipeline } from "@shared/schema";
⋮----
const handleFileUpload = (file: File) =>
const handleRunPipeline = () =>
const handleModelToggle = (model: string, checked: boolean) =>
const getCurrentStep = () =>
const getBestResult = () =>
⋮----
currentStep=
⋮----
checked=
```

## File: client/src/pages/not-found.tsx
```typescript
import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";
export default function NotFound()
```

## File: drizzle.config.ts
```typescript
import { defineConfig } from "drizzle-kit";
```

## File: package.json
```json
{
  "name": "rest-express",
  "version": "1.0.0",
  "type": "module",
  "license": "MIT",
  "scripts": {
    "dev": "NODE_ENV=development tsx server/index.ts",
    "build": "vite build && esbuild server/index.ts --platform=node --packages=external --bundle --format=esm --outdir=dist",
    "start": "NODE_ENV=production node dist/index.js",
    "check": "tsc",
    "db:push": "drizzle-kit push"
  },
  "dependencies": {
    "@hookform/resolvers": "^3.10.0",
    "@jridgewell/trace-mapping": "^0.3.25",
    "@neondatabase/serverless": "^0.10.4",
    "@playwright/test": "^1.55.0",
    "@radix-ui/react-accordion": "^1.2.4",
    "@radix-ui/react-alert-dialog": "^1.1.7",
    "@radix-ui/react-aspect-ratio": "^1.1.3",
    "@radix-ui/react-avatar": "^1.1.4",
    "@radix-ui/react-checkbox": "^1.1.5",
    "@radix-ui/react-collapsible": "^1.1.4",
    "@radix-ui/react-context-menu": "^2.2.7",
    "@radix-ui/react-dialog": "^1.1.7",
    "@radix-ui/react-dropdown-menu": "^2.1.7",
    "@radix-ui/react-hover-card": "^1.1.7",
    "@radix-ui/react-label": "^2.1.3",
    "@radix-ui/react-menubar": "^1.1.7",
    "@radix-ui/react-navigation-menu": "^1.2.6",
    "@radix-ui/react-popover": "^1.1.7",
    "@radix-ui/react-progress": "^1.1.3",
    "@radix-ui/react-radio-group": "^1.2.4",
    "@radix-ui/react-scroll-area": "^1.2.4",
    "@radix-ui/react-select": "^2.1.7",
    "@radix-ui/react-separator": "^1.1.3",
    "@radix-ui/react-slider": "^1.2.4",
    "@radix-ui/react-slot": "^1.2.0",
    "@radix-ui/react-switch": "^1.1.4",
    "@radix-ui/react-tabs": "^1.1.4",
    "@radix-ui/react-toast": "^1.2.7",
    "@radix-ui/react-toggle": "^1.1.3",
    "@radix-ui/react-toggle-group": "^1.1.3",
    "@radix-ui/react-tooltip": "^1.2.0",
    "@tanstack/react-query": "^5.60.5",
    "@types/multer": "^2.0.0",
    "@types/supertest": "^6.0.3",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "cmdk": "^1.1.1",
    "connect-pg-simple": "^10.0.0",
    "date-fns": "^3.6.0",
    "drizzle-orm": "^0.39.1",
    "drizzle-zod": "^0.7.0",
    "embla-carousel-react": "^8.6.0",
    "express": "^4.21.2",
    "express-session": "^1.18.1",
    "framer-motion": "^11.13.1",
    "input-otp": "^1.4.2",
    "lucide-react": "^0.453.0",
    "memorystore": "^1.6.7",
    "multer": "^2.0.2",
    "next-themes": "^0.4.6",
    "openai": "^5.20.2",
    "passport": "^0.7.0",
    "passport-local": "^1.0.0",
    "react": "^18.3.1",
    "react-day-picker": "^8.10.1",
    "react-dom": "^18.3.1",
    "react-dropzone": "^14.3.8",
    "react-hook-form": "^7.55.0",
    "react-icons": "^5.4.0",
    "react-resizable-panels": "^2.1.7",
    "recharts": "^2.15.2",
    "supertest": "^7.1.4",
    "tailwind-merge": "^2.6.0",
    "tailwindcss-animate": "^1.0.7",
    "tw-animate-css": "^1.2.5",
    "vaul": "^1.1.2",
    "vitest": "^3.2.4",
    "wouter": "^3.3.5",
    "ws": "^8.18.0",
    "zod": "^3.24.2",
    "zod-validation-error": "^3.4.0"
  },
  "devDependencies": {
    "@replit/vite-plugin-cartographer": "^0.3.0",
    "@replit/vite-plugin-dev-banner": "^0.1.1",
    "@replit/vite-plugin-runtime-error-modal": "^0.0.3",
    "@tailwindcss/typography": "^0.5.15",
    "@tailwindcss/vite": "^4.1.3",
    "@types/connect-pg-simple": "^7.0.3",
    "@types/express": "4.17.21",
    "@types/express-session": "^1.18.0",
    "@types/node": "20.16.11",
    "@types/passport": "^1.0.16",
    "@types/passport-local": "^1.0.38",
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.1",
    "@types/ws": "^8.5.13",
    "@vitejs/plugin-react": "^4.3.2",
    "autoprefixer": "^10.4.20",
    "drizzle-kit": "^0.30.4",
    "esbuild": "^0.25.0",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.17",
    "tsx": "^4.19.1",
    "typescript": "5.6.3",
    "vite": "^5.4.19"
  },
  "optionalDependencies": {
    "bufferutil": "^4.0.8"
  }
}
```

## File: server/index.ts
```typescript
import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
```

## File: server/routes.ts
```typescript
import type { Express } from "express";
import { createServer, type Server } from "http";
import multer from "multer";
import { storage } from "./storage";
import { pipelineService } from "./services/pipeline";
import { insertPipelineSchema, updatePipelineSchema } from "@shared/schema";
⋮----
export async function registerRoutes(app: Express): Promise<Server>
```

## File: server/services/openai.ts
```typescript
import OpenAI from "openai";
⋮----
export interface PersonaAnalysis {
  tone: string;
  style: string;
  quirks: string;
  personality: string;
}
export interface ModelScore {
  toneScore: number;
  styleScore: number;
  personalityScore: number;
  averageScore: number;
}
export async function analyzePersona(transcript: string): Promise<PersonaAnalysis>
export function generateSystemPrompt(analysis: PersonaAnalysis, examples: string = ""): string
export async function testModelWithPrompt(
  modelName: string,
  systemPrompt: string,
  question: string
): Promise<string>
export async function judgeResponse(
  systemPrompt: string,
  question: string,
  modelResponse: string
): Promise<ModelScore>
export async function generateJudgeComments(
  bestModel: string,
  bestScore: ModelScore
): Promise<string>
```

## File: server/services/pipeline.ts
```typescript
import { analyzePersona, generateSystemPrompt, testModelWithPrompt, judgeResponse, generateJudgeComments, type PersonaAnalysis, type ModelScore } from './openai';
import { storage } from '../storage';
import { type EvaluationResult, type Pipeline } from '@shared/schema';
export class PipelineService
⋮----
async runPersonaAnalysis(pipelineId: string): Promise<void>
async runModelEvaluation(pipelineId: string): Promise<void>
async getProgress(pipelineId: string): Promise<
```

## File: server/storage.ts
```typescript
import { type User, type InsertUser, type Pipeline, type InsertPipeline, type UpdatePipeline } from "@shared/schema";
import { randomUUID } from "crypto";
export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getPipeline(id: string): Promise<Pipeline | undefined>;
  createPipeline(pipeline: InsertPipeline): Promise<Pipeline>;
  updatePipeline(id: string, updates: UpdatePipeline): Promise<Pipeline>;
  getAllPipelines(): Promise<Pipeline[]>;
}
⋮----
getUser(id: string): Promise<User | undefined>;
getUserByUsername(username: string): Promise<User | undefined>;
createUser(user: InsertUser): Promise<User>;
getPipeline(id: string): Promise<Pipeline | undefined>;
createPipeline(pipeline: InsertPipeline): Promise<Pipeline>;
updatePipeline(id: string, updates: UpdatePipeline): Promise<Pipeline>;
getAllPipelines(): Promise<Pipeline[]>;
⋮----
export class MemStorage implements IStorage
⋮----
constructor()
async getUser(id: string): Promise<User | undefined>
async getUserByUsername(username: string): Promise<User | undefined>
async createUser(insertUser: InsertUser): Promise<User>
async getPipeline(id: string): Promise<Pipeline | undefined>
async createPipeline(insertPipeline: InsertPipeline): Promise<Pipeline>
async updatePipeline(id: string, updates: UpdatePipeline): Promise<Pipeline>
async getAllPipelines(): Promise<Pipeline[]>
```

## File: server/vite.ts
```typescript
import express, { type Express } from "express";
import fs from "fs";
import path from "path";
import { createServer as createViteServer, createLogger } from "vite";
import { type Server } from "http";
import viteConfig from "../vite.config";
import { nanoid } from "nanoid";
⋮----
export function log(message: string, source = "express")
export async function setupVite(app: Express, server: Server)
export function serveStatic(app: Express)
```

## File: shared/schema.ts
```typescript
import { sql } from "drizzle-orm";
import { pgTable, text, varchar, jsonb, timestamp, real } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";
⋮----
status: text("status").notNull().default("pending"), // pending, analyzing, evaluating, complete, error
⋮----
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type Pipeline = typeof pipelines.$inferSelect;
export type InsertPipeline = z.infer<typeof insertPipelineSchema>;
export type UpdatePipeline = z.infer<typeof updatePipelineSchema>;
export interface PersonaAnalysis {
  tone: string;
  style: string;
  quirks: string;
  personality: string;
}
export interface EvaluationResult {
  modelName: string;
  averageScore: number;
  toneScore: number;
  styleScore: number;
  personalityScore: number;
  responses: Array<{
    question: string;
    response: string;
    score: number;
  }>;
}
export interface PipelineProgress {
  step: 'upload' | 'analyze' | 'evaluate' | 'complete';
  progress: number;
  message: string;
}
```

## File: tsconfig.json
```json
{
  "include": ["client/src/**/*", "shared/**/*", "server/**/*"],
  "exclude": ["node_modules", "build", "dist", "**/*.test.ts"],
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": "./node_modules/typescript/tsbuildinfo",
    "noEmit": true,
    "module": "ESNext",
    "strict": true,
    "lib": ["esnext", "dom", "dom.iterable"],
    "jsx": "preserve",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "allowImportingTsExtensions": true,
    "moduleResolution": "bundler",
    "baseUrl": ".",
    "types": ["node", "vite/client"],
    "paths": {
      "@/*": ["./client/src/*"],
      "@shared/*": ["./shared/*"]
    }
  }
}
```

## File: vite.config.ts
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import runtimeErrorOverlay from "@replit/vite-plugin-runtime-error-modal";
```
