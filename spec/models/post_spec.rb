# == Schema Information
#
# Table name: posts
#
#  id           :integer          not null, primary key
#  description  :text
#  published_at :datetime         not null
#  link         :string           not null
#  title        :string           not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#  source_id    :integer
#  state        :string           default("pending"), not null
#
# Indexes
#
#  index_posts_on_published_at  (published_at)
#  index_posts_on_source_id     (source_id)
#

require "rails_helper"

describe Post do
  subject { described_class.new(topic: topic) }
  let(:topic) { build(:topic, posts: [post]) }
  let(:post) { build(:post) }

  %i(title published_at link).each do |field|
    it { is_expected.to validate_presence_of(field) }
  end

  describe "#same_posts" do
    it "" do
      allow(topic).to receive_message_chain(:posts, :ordered_by_date).and_return([subject, post])

      expect(subject.same_posts).to eql([post])
    end
  end
end
