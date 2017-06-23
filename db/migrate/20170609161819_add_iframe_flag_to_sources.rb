class AddIframeFlagToSources < ActiveRecord::Migration[5.0]
  def change
    add_column :sources, :iframe_flag, :boolean, default: true
  end
end
