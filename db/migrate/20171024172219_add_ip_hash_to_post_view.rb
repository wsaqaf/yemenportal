class AddIpHashToPostView < ActiveRecord::Migration[5.0]
  def change
    add_column :post_views, :ip_hash, :string, null: true
  end
end
