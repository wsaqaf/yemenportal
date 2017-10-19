require "rails_helper"

describe Topic do
  describe "relations" do
    it { is_expected.to belong_to(:main_post).class_name("Post") }
    it { is_expected.to have_many(:posts).dependent(:destroy) }
  end

  describe "#related_posts" do
    subject { topic.related_posts }

    let(:main_post) { create(:post) }
    let(:topic) { create(:topic, main_post: main_post) }
    let!(:related_post) { create(:post, topic: topic) }

    it "returns all topics except main" do
      is_expected.to match([related_post])
    end
  end
end
