# ComparisonView.xaml (Full Reference)

This is the full XAML example referenced from `SKILL.md`.

```xml
<UserControl x:Class="YourApp.Views.ComparisonView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <UserControl.Resources>
        <Style x:Key="FieldNameStyle" TargetType="TextBlock">
            <Setter Property="FontSize" Value="11"/>
            <Setter Property="Padding" Value="5,2"/>
            <Setter Property="Background" Value="#F5F5F5"/>
        </Style>
        <Style x:Key="ValueStyle" TargetType="TextBlock">
            <Setter Property="FontSize" Value="11"/>
            <Setter Property="Padding" Value="5,2"/>
            <Setter Property="TextWrapping" Value="Wrap"/>
        </Style>
    </UserControl.Resources>

    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>

        <TextBlock Grid.Row="0" FontSize="16" FontWeight="Bold"
                   Text="Comparison Results" Margin="0,0,0,10"/>

        <ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto">
            <ItemsControl ItemsSource="{Binding ComparisonItems}">
                <ItemsControl.ItemTemplate>
                    <DataTemplate>
                        <Border BorderBrush="#CCCCCC" BorderThickness="1"
                                Margin="0,0,0,15" Padding="10"
                                Background="#FAFAFA" CornerRadius="5">
                            <StackPanel>
                                <!-- Score Header -->
                                <Grid Margin="0,0,0,10">
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="Auto"/>
                                    </Grid.ColumnDefinitions>
                                    <TextBlock Grid.Column="0" FontSize="14" FontWeight="Bold"
                                               Text="{Binding Index, StringFormat='#{0}'}"/>
                                    <StackPanel Grid.Column="1" Orientation="Horizontal">
                                        <TextBlock Text="Score: " FontSize="12"/>
                                        <TextBlock Text="{Binding ScorePercent, StringFormat={}{0:F1}%}"
                                                   FontSize="12" FontWeight="Bold"
                                                   Foreground="{Binding ScoreColor}"/>
                                    </StackPanel>
                                </Grid>

                                <Separator Margin="0,0,0,10"/>

                                <!-- 3-Column Comparison Grid -->
                                <Grid>
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="140"/> <!-- Field Name -->
                                        <ColumnDefinition Width="*"/>   <!-- Source A -->
                                        <ColumnDefinition Width="*"/>   <!-- Source B -->
                                    </Grid.ColumnDefinitions>

                                    <!-- Column Headers -->
                                    <TextBlock Grid.Column="0" Grid.Row="0"
                                               Text="Field" FontWeight="Bold" FontSize="11"/>
                                    <TextBlock Grid.Column="1" Grid.Row="0"
                                               Text="Source A" FontWeight="Bold" FontSize="11"/>
                                    <TextBlock Grid.Column="2" Grid.Row="0"
                                               Text="Source B" FontWeight="Bold" FontSize="11"/>

                                    <!-- Field Row Example -->
                                    <TextBlock Grid.Column="0" Grid.Row="1"
                                               Text="Field 1" Style="{StaticResource FieldNameStyle}"/>
                                    <TextBlock Grid.Column="1" Grid.Row="1"
                                               Text="{Binding SourceAField1}"
                                               Style="{StaticResource ValueStyle}"/>
                                    <TextBlock Grid.Column="2" Grid.Row="1"
                                               Text="{Binding SourceBField1}"
                                               Background="{Binding SourceBField1Background}"
                                               Style="{StaticResource ValueStyle}"/>

                                    <!-- Add Grid.RowDefinitions and more rows per field... -->
                                </Grid>
                            </StackPanel>
                        </Border>
                    </DataTemplate>
                </ItemsControl.ItemTemplate>
            </ItemsControl>
        </ScrollViewer>
    </Grid>
</UserControl>
```
