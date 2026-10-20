// Compile-time stand-ins only. The user's real XAML and settings were not supplied.
namespace ToolBox.Pages
{
    public partial class SpriteSplitter
    {
        private readonly System.Windows.Controls.TextBlock TxtExportPath = new System.Windows.Controls.TextBlock();
        private readonly System.Windows.Controls.TextBlock TxtStatus = new System.Windows.Controls.TextBlock();
        private readonly System.Windows.Controls.Button BtnPickImage = new System.Windows.Controls.Button();
        private readonly System.Windows.Controls.Button BtnExport = new System.Windows.Controls.Button();
        private readonly System.Windows.Controls.ItemsControl SpriteItemsControl = new System.Windows.Controls.ItemsControl();
        private void InitializeComponent() { }
    }
}
namespace ToolBox.Properties
{
    internal sealed class Settings
    {
        internal static readonly Settings Default = new Settings();
        internal string ExportFolder { get; set; }
        internal void Save() { }
    }
}
