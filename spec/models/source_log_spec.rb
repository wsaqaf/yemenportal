# == Schema Information
#
# Table name: source_logs
#
#  id          :integer          not null, primary key
#  state       :string
#  source_id   :integer          not null
#  posts_count :integer          default("0")
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_source_logs_on_source_id  (source_id)
#

require "rails_helper"

RSpec.describe SourceLog, type: :model do
  pending "add some examples to (or delete) #{__FILE__}"
end
