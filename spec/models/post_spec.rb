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
  %i(published_at link).each do |field|
    it { is_expected.to validate_presence_of(field) }
  end

  describe ".ordered_by_coverage" do
    subject { described_class.ordered_by_coverage }

    let(:main_post) { create(:post, :main_post) }

    context "when there are a main post and related post of topic" do
      let!(:related_post) { create(:post, topic: main_post.topic) }

      it "gives priority to main post in order" do
        is_expected.to eq([main_post, related_post])
      end
    end

    context "when there are two main posts" do
      let(:another_main_post) { create(:post, :main_post) }
      let!(:related_post) { create(:post, topic: another_main_post.topic) }

      it "orders them by topic size" do
        is_expected.to eq([another_main_post, main_post, related_post])
      end
    end
  end

  describe ".include_voted_by_user" do
    it "returns posts with upvoted_by_user and downvoted_by_user attributes" do
      user = create(:user)
      post_voted_by_user = create(:post)
      Vote.create(post: post_voted_by_user, user: user, value: 1)

      another_user = create(:user)
      post_not_voted_by_user = create(:post)
      Vote.create(post: post_voted_by_user, user: another_user, value: 1)
      Vote.create(post: post_not_voted_by_user, user: another_user, value: 1)

      post_downvoted_by_user = create(:post)
      Vote.create(post: post_downvoted_by_user, user: user, value: -1)

      posts = Post.include_voted_by_user(user)

      expect(posts.first.upvoted_by_user?).to eq(true)
      expect(posts.second.upvoted_by_user?).to eq(false)
      expect(posts.third.downvoted_by_user?).to eq(true)
    end
  end

  describe "#update_voting_result" do
    it "updates voting_result to received value" do
      post = Post.new

      expect(post).to receive(:update).with(voting_result: 42)

      post.update_voting_result(42)
    end
  end
end
