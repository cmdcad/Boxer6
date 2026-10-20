using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using Point = System.Drawing.Point;
using Rectangle = System.Drawing.Rectangle;

namespace ToolBox.Pages
{
    // Uses the same XAML controls, event names and ExportFolder setting as the original.
    public partial class SpriteSplitter : Page
    {
        private readonly List<Bitmap> _processedBitmaps = new List<Bitmap>();
        private string _exportDirectory = string.Empty;
        private bool _busy;

        // Configure these for the actual sheet; do not assume all sheets are 3x3.
        public int SpriteRows { get; set; } = 3;
        public int SpriteColumns { get; set; } = 3;
        public int MaximumSpeckPixels { get; set; } = 12;
        // Safe default: existing alpha is authoritative. Enable explicitly for
        // binary-alpha cutouts with known pale fringes, such as the nine samples.
        public bool CleanExistingAlphaEdges { get; set; } = false;

        public SpriteSplitter()
        {
            InitializeComponent();
            LoadOrInitializeExportPath();
        }

        private void LoadOrInitializeExportPath()
        {
            string saved = Properties.Settings.Default.ExportFolder;
            if (string.IsNullOrWhiteSpace(saved) || !Directory.Exists(saved))
                saved = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyPictures), "ExportedSprites");
            _exportDirectory = saved;
            TxtExportPath.Text = saved;
        }

        private void BtnChangeFolder_Click(object sender, RoutedEventArgs e)
        {
            if (_busy) return;
            using (var dialog = new System.Windows.Forms.FolderBrowserDialog())
            {
                dialog.Description = "Select Export Folder";
                dialog.SelectedPath = _exportDirectory;
                if (dialog.ShowDialog() != System.Windows.Forms.DialogResult.OK) return;
                _exportDirectory = dialog.SelectedPath;
                TxtExportPath.Text = _exportDirectory;
                Properties.Settings.Default.ExportFolder = _exportDirectory;
                Properties.Settings.Default.Save();
            }
        }

        private void SetBusy(bool value)
        {
            _busy = value;
            BtnPickImage.IsEnabled = !value;
            BtnExport.IsEnabled = !value && _processedBitmaps.Count > 0;
        }

        private async void BtnPickImage_Click(object sender, RoutedEventArgs e)
        {
            if (_busy) return;
            var dialog = new OpenFileDialog
            {
                Filter = "Image Files|*.png;*.jpg;*.jpeg|All files|*.*",
                Title = "Select Sprite Sheet Image"
            };
            if (dialog.ShowDialog() != true) return;
            SetBusy(true);
            TxtStatus.Text = "Processing sprites...";
            TxtStatus.Visibility = Visibility.Visible;
            List<Bitmap> pending = null;
            try
            {
                int rows = SpriteRows, cols = SpriteColumns, specks = MaximumSpeckPixels;
                bool cleanExisting = CleanExistingAlphaEdges;
                pending = await Task.Run(() => ProcessSheet(dialog.FileName, rows, cols, specks, cleanExisting));
                var previews = new List<BitmapImage>();
                foreach (Bitmap bitmap in pending) previews.Add(ConvertToBitmapImage(bitmap));
                foreach (Bitmap old in _processedBitmaps) old.Dispose();
                _processedBitmaps.Clear();
                _processedBitmaps.AddRange(pending);
                pending = null; // Ownership transferred only after successful processing.
                SpriteItemsControl.ItemsSource = previews;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to process image: " + ex.Message, "Sprite processing failed");
            }
            finally
            {
                if (pending != null) foreach (Bitmap bitmap in pending) bitmap.Dispose();
                TxtStatus.Visibility = Visibility.Collapsed;
                SetBusy(false);
            }
        }

        private static List<Bitmap> ProcessSheet(string path, int rows, int cols, int specks, bool cleanExisting)
        {
            if (rows < 1 || cols < 1 || specks < 0) throw new ArgumentOutOfRangeException("Invalid grid or speck threshold.");
            var result = new List<Bitmap>();
            try
            {
                using (var sheet = new Bitmap(path))
                {
                    if (rows > sheet.Height || cols > sheet.Width) throw new ArgumentException("Grid cells must have positive dimensions.");
                    for (int r = 0; r < rows; r++)
                    for (int c = 0; c < cols; c++)
                    {
                        // Include remainder pixels instead of discarding the right/bottom edge.
                        int x0 = c * sheet.Width / cols, x1 = (c + 1) * sheet.Width / cols;
                        int y0 = r * sheet.Height / rows, y1 = (r + 1) * sheet.Height / rows;
                        Bitmap frame = sheet.Clone(new Rectangle(x0, y0, x1 - x0, y1 - y0), PixelFormat.Format32bppArgb);
                        result.Add(frame); // Dispose even this frame if processing fails.
                        byte[] pixels = ReadPixels(frame);
                        bool hasAlpha = false, hasPartialAlpha = false;
                        for (int i = 3; i < pixels.Length; i += 4)
                        {
                            hasAlpha |= pixels[i] < 255;
                            hasPartialAlpha |= pixels[i] > 0 && pixels[i] < 255;
                        }
                        if (!hasAlpha) RemoveBorderCheckerboard(pixels, frame.Width, frame.Height);
                        if (!hasAlpha || (cleanExisting && !hasPartialAlpha))
                        {
                            pixels = ReconstructNeutralFringes(pixels, frame.Width, frame.Height);
                            RemoveSmallIslands(pixels, frame.Width, frame.Height, specks);
                            for (int i = 0; i < pixels.Length; i += 4)
                                if (pixels[i + 3] == 0) pixels[i] = pixels[i + 1] = pixels[i + 2] = 0;
                            WritePixels(frame, pixels);
                        }
                    }
                }
                return result;
            }
            catch
            {
                foreach (Bitmap bitmap in result) bitmap.Dispose();
                throw;
            }
        }

        private async void BtnExport_Click(object sender, RoutedEventArgs e)
        {
            if (_busy || _processedBitmaps.Count == 0) return;
            SetBusy(true);
            try
            {
                string destination = _exportDirectory;
                // Picking another sheet is blocked while these owned bitmaps are read.
                await Task.Run(() =>
                {
                    Directory.CreateDirectory(destination);
                    for (int i = 0; i < _processedBitmaps.Count; i++)
                        _processedBitmaps[i].Save(Path.Combine(destination, "sprite_frame_" + (i + 1).ToString("D2") + ".png"), ImageFormat.Png);
                });
                MessageBox.Show("Saved " + _processedBitmaps.Count + " PNG frames to:\n" + destination, "Export complete");
            }
            catch (Exception ex) { MessageBox.Show("Export failed: " + ex.Message); }
            finally { SetBusy(false); }
        }

        private static byte[] ReadPixels(Bitmap bitmap)
        {
            var rect = new Rectangle(0, 0, bitmap.Width, bitmap.Height);
            BitmapData data = bitmap.LockBits(rect, ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            try
            {
                int rowBytes = bitmap.Width * 4;
                var pixels = new byte[rowBytes * bitmap.Height];
                for (int y = 0; y < bitmap.Height; y++)
                    Marshal.Copy(IntPtr.Add(data.Scan0, y * data.Stride), pixels, y * rowBytes, rowBytes);
                return pixels;
            }
            finally { bitmap.UnlockBits(data); }
        }

        private static void WritePixels(Bitmap bitmap, byte[] pixels)
        {
            var rect = new Rectangle(0, 0, bitmap.Width, bitmap.Height);
            BitmapData data = bitmap.LockBits(rect, ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);
            try
            {
                int rowBytes = bitmap.Width * 4;
                for (int y = 0; y < bitmap.Height; y++)
                    Marshal.Copy(pixels, y * rowBytes, IntPtr.Add(data.Scan0, y * data.Stride), rowBytes);
            }
            finally { bitmap.UnlockBits(data); }
        }

        private static bool IsMatte(byte[] p, int i, int minimum, int tolerance)
        {
            int lo = Math.Min(p[i], Math.Min(p[i + 1], p[i + 2]));
            int hi = Math.Max(p[i], Math.Max(p[i + 1], p[i + 2]));
            return lo > minimum && hi - lo < tolerance;
        }

        private static void RemoveBorderCheckerboard(byte[] source, int width, int height)
        {
            var queued = new bool[width * height];
            var queue = new Queue<int>();
            Action<int, int> add = (x, y) =>
            {
                if (x < 0 || x >= width || y < 0 || y >= height) return;
                int n = y * width + x;
                if (!queued[n] && IsMatte(source, n * 4, 150, 20))
                { queued[n] = true; queue.Enqueue(n); }
            };
            for (int x = 0; x < width; x++) { add(x, 0); add(x, height - 1); }
            for (int y = 0; y < height; y++) { add(0, y); add(width - 1, y); }
            while (queue.Count > 0)
            {
                int n = queue.Dequeue(), x = n % width, y = n / width;
                source[n * 4 + 3] = 0;
                add(x - 1, y); add(x + 1, y); add(x, y - 1); add(x, y + 1);
            }
        }

        private static byte[] ReconstructNeutralFringes(byte[] source, int width, int height)
        {
            byte[] output = (byte[])source.Clone();
            for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
            {
                int i = (y * width + x) * 4;
                if (source[i + 3] == 0 || !IsMatte(source, i, 130, 25)) continue;
                bool boundary = false;
                for (int dy = -1; dy <= 1; dy++)
                for (int dx = -1; dx <= 1; dx++)
                {
                    int xx = x + dx, yy = y + dy;
                    if (xx < 0 || xx >= width || yy < 0 || yy >= height || source[(yy * width + xx) * 4 + 3] == 0) boundary = true;
                }
                if (!boundary) continue;
                int foreground = -1, nearest = int.MaxValue, backgroundCount = 0;
                double[] background = new double[3];
                for (int dy = -2; dy <= 2; dy++)
                for (int dx = -2; dx <= 2; dx++)
                {
                    int xx = x + dx, yy = y + dy;
                    if (xx < 0 || xx >= width || yy < 0 || yy >= height) continue;
                    int j = (yy * width + xx) * 4;
                    int lo = Math.Min(source[j], Math.Min(source[j + 1], source[j + 2]));
                    int hi = Math.Max(source[j], Math.Max(source[j + 1], source[j + 2]));
                    int distance = dx * dx + dy * dy;
                    if (source[j + 3] > 0 && lo < 90 && hi - lo < 60 && distance < nearest)
                    { foreground = j; nearest = distance; }
                    if (source[j + 3] == 0 && IsMatte(source, j, 140, 25))
                    {
                        for (int k = 0; k < 3; k++) background[k] += source[j + k];
                        backgroundCount++;
                    }
                }
                if (foreground < 0) continue;
                double numerator = 0, denominator = 0;
                for (int k = 0; k < 3; k++)
                {
                    double b = backgroundCount == 0 ? 255 : background[k] / backgroundCount;
                    double v = source[foreground + k] - b;
                    numerator += (source[i + k] - b) * v;
                    denominator += v * v;
                }
                if (denominator < 100) continue;
                double coverage = Math.Max(0, Math.Min(1, numerator / denominator));
                for (int k = 0; k < 3; k++) output[i + k] = source[foreground + k];
                output[i + 3] = (byte)Math.Round(source[i + 3] * coverage);
            }
            return output;
        }

        private static void RemoveSmallIslands(byte[] pixels, int width, int height, int maximum)
        {
            if (maximum == 0) return;
            var seen = new bool[width * height];
            for (int start = 0; start < seen.Length; start++)
            {
                if (seen[start] || pixels[start * 4 + 3] == 0) continue;
                var queue = new Queue<int>();
                var component = new List<int>();
                queue.Enqueue(start); seen[start] = true;
                while (queue.Count > 0)
                {
                    int n = queue.Dequeue(), x = n % width, y = n / width;
                    component.Add(n);
                    for (int dy = -1; dy <= 1; dy++)
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        int xx = x + dx, yy = y + dy;
                        if (xx < 0 || xx >= width || yy < 0 || yy >= height) continue;
                        int next = yy * width + xx;
                        if (!seen[next] && pixels[next * 4 + 3] > 0)
                        { seen[next] = true; queue.Enqueue(next); }
                    }
                }
                if (component.Count <= maximum)
                    foreach (int n in component)
                        for (int k = 0; k < 4; k++) pixels[n * 4 + k] = 0;
            }
        }

        private static BitmapImage ConvertToBitmapImage(Bitmap source)
        {
            using (var memory = new MemoryStream())
            {
                source.Save(memory, ImageFormat.Png);
                memory.Position = 0;
                var image = new BitmapImage();
                image.BeginInit();
                image.StreamSource = memory;
                image.CacheOption = BitmapCacheOption.OnLoad;
                image.EndInit();
                image.Freeze();
                return image;
            }
        }
    }
}
