class AddLogoUrlToSources < ActiveRecord::Migration[5.0]
  def change
    add_column :sources, :logo_url, :string
  end
end
