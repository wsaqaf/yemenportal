class VotesAreForTopicsNotForPosts < ActiveRecord::Migration[5.0]
  def change
    drop_table(:votes)
    create_table(:votes) do |t|
      t.references :user, null: false, foreign_key: { on_delete: :cascade }
      t.references :topic, null: false, foreign_key: { on_delete: :cascade }
      t.integer :value

      t.timestamps
    end
    add_column(:topics, :voting_result, :integer, default: 0)
    add_index(:topics, :voting_result)
  end
end
