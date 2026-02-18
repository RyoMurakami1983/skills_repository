# OcrProcessTabView.xaml (Full Reference)

This is the full XAML example referenced from `SKILL.md`.

```xml
<UserControl x:Class="YourApp.Views.OcrProcessTabView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>  <!-- Input Fields -->
            <RowDefinition Height="Auto"/>  <!-- Progress Bar -->
            <RowDefinition Height="*"/>     <!-- Progress Log -->
            <RowDefinition Height="Auto"/>  <!-- Start Button -->
        </Grid.RowDefinitions>

        <!-- Input Fields (customize per use case) -->
        <StackPanel Grid.Row="0" Margin="10">
            <TextBlock Text="Category" FontWeight="Bold"/>
            <ComboBox ItemsSource="{Binding CategoryItems}"
                      SelectedItem="{Binding SelectedCategory}"
                      Margin="0,4,0,10"/>

            <TextBlock Text="Document Type" FontWeight="Bold"/>
            <ComboBox ItemsSource="{Binding TypeItems}"
                      SelectedItem="{Binding SelectedType}"
                      Margin="0,4,0,10"/>

            <TextBlock Text="Remarks" FontWeight="Bold"/>
            <TextBox Text="{Binding Remarks, UpdateSourceTrigger=PropertyChanged}"
                     AcceptsReturn="True" Height="60"
                     Margin="0,4,0,0"/>
        </StackPanel>

        <!-- Progress Bar with Percentage Overlay -->
        <Grid Grid.Row="1" Margin="10,5">
            <ProgressBar Value="{Binding ProgressValue}" Maximum="100" Height="20"/>
            <TextBlock Text="{Binding ProgressValue, StringFormat='{}{0}%'}"
                       HorizontalAlignment="Center" VerticalAlignment="Center"
                       FontWeight="Bold"/>
        </Grid>

        <!-- Progress Log -->
        <ListView Grid.Row="2" ItemsSource="{Binding ProgressItems}" Margin="10,5">
            <ListView.View>
                <GridView>
                    <GridViewColumn Header="Time" Width="80"
                        DisplayMemberBinding="{Binding Timestamp, StringFormat='{}{0:HH:mm:ss}'}"/>
                    <GridViewColumn Header="" Width="30"
                        DisplayMemberBinding="{Binding Icon}"/>
                    <GridViewColumn Header="Message" Width="200"
                        DisplayMemberBinding="{Binding Message}"/>
                    <GridViewColumn Header="Status" Width="80"
                        DisplayMemberBinding="{Binding Status}"/>
                </GridView>
            </ListView.View>
        </ListView>

        <!-- Start Button (enabled after PDF upload) -->
        <Button Grid.Row="3" Content="Start OCR"
                Command="{Binding StartOcrCommand}"
                Background="#4CAF50" Foreground="White" FontWeight="Bold"
                Margin="10" Padding="15,8" FontSize="14"/>
    </Grid>
</UserControl>
```
