# Updated SpriteSplitter code-behind

SpriteSplitter.xaml.cs replaces the supplied ToolBox.Pages.SpriteSplitter code-behind. Keep the existing SpriteSplitter.xaml, named controls and Properties.Settings.Default.ExportFolder setting. Back up the original file before replacing it in the WPF tool. This file is not part of the Swift app.

Defaults: SpriteRows=3, SpriteColumns=3, MaximumSpeckPixels=12. Set the grid to the actual source layout. For one already-extracted image, set rows and columns to1.

CleanExistingAlphaEdges defaults to false to protect existing alpha. For the nine known binary-alpha images with pale fringes, explicitly set CleanExistingAlphaEdges=true before selecting the image. Existing partial alpha is still preserved rather than re-keyed. Opaque sheets receive border-connected neutral-background removal and a conservative fringe pass. The neutral-matte detector is intended for the provided gray/white checkerboard, not arbitrary photos or backgrounds.

The fringe pass reads an immutable BGRA snapshot, estimates local background/outline colors and reconstructs fractional alpha. The C# version averages nearby background samples; the Python prototype uses a median. Outputs need not match byte-for-byte. Small-island removal uses8-connected components and a configurable threshold;12 is calibrated to the supplied341x227 samples, not universal. The method cannot guarantee perfect reconstruction from flattened artwork or remove all enclosed checkerboard islands.

Export keeps the original sprite_frame_XX.png naming and can overwrite same-named files in the selected folder. Choose a separate export folder when preserving originals.

Validation: dotnet build CompileCheck/CompileCheck.csproj --ignore-failed-sources -p:NuGetAudit=false -v:quiet succeeded with0 warnings and0 errors using installed.NET9 Windows Desktop references on2026-10-20. CompileCheck supplies stand-ins for the missing XAML controls and settings. The user's actual WPF project and interactive UI were not built/run; verify its target framework, XAML names and settings during integration. No external NuGet packages are required by this replacement.
