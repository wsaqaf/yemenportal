class AddViewsToPost < ActiveRecord::Migration[5.0]
  def change
    create_post_views_table
    add_views_count_to_posts
  end

  private

  def create_post_views_table
    create_table :post_views do |t|
      t.references :post, null: false, foreign_key: { on_delete: :cascade }
      t.references :user, null: true, foreign_key: { on_delete: :nullify }
      t.timestamps
    end
  end

  def add_views_count_to_posts
    add_column :posts, :post_views_count, :integer, null: false, default: 0
  end
end
