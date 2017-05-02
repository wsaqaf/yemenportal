class AddApproveStateToSource < ActiveRecord::Migration[5.0]
  def up
    add_column :sources, :approve_state, :string, default: 'suggested'
    add_reference :sources, :user, foreign_key: true

    Source.all.each do |source|
      source.update(approve_state: 'approved') if source.approve_state == 'suggested'
    end
  end

  def down
    remove_column :sources, :approve_state
    remove_reference :sources, :user, foreign_key: true
  end
end
