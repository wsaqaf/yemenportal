require "rails_helper"

RSpec.describe PostsFetcher::TopicAttacher do
  describe "#attach" do
    let(:topic) { create(:topic) }
    let(:main_post) { topic.main_post }
    let(:attaching_post) { create(:post, published_at: post_publish_date) }

    before { described_class.new(post: attaching_post, topic: topic).attach }

    context "when attaching topic publish date is early than main topic post" do
      let(:post_publish_date) { main_post.published_at - 1.day }

      it "attaches new post as main post of topic" do
        expect(topic.main_post).to be(attaching_post)
        expect(attaching_post.related_posts).to match([main_post])
      end
    end

    context "when attaching topic publish date isn't early than main topic post" do
      let(:post_publish_date) { main_post.published_at + 1.day }

      it "attaches new post as related" do
        expect(topic.main_post).to be(main_post)
        expect(main_post.related_posts).to match([attaching_post])
      end
    end
  end
end
