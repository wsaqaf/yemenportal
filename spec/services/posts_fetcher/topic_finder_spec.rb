require "rails_helper"

RSpec.describe PostsFetcher::TopicFinder do
  describe "#attach_topic!" do
    subject { described_class.new(post).attach_topic! }

    context "when post item is invalid" do
      let(:post) { build(:post, link: nil) }

      it { is_expected.to be_nil }
    end

    context "when post item is valid" do
      let(:post) { create(:post) }

      shared_examples "creator of new topic" do
        it "creates new topic" do
          expect { subject }.to change { Topic.count }
        end

        it "makes new post the main post of topic" do
          subject
          expect(post.topic).to be_present
          expect(post.main_topic).to be_present
        end
      end

      context "when there is a topic for post" do
        let(:related_topic) { create(:topic) }

        before do
          allow(PostsFetcher::RelatedPostsFinder)
            .to receive_message_chain(:new, :topic_with_related_posts_or_nil)
            .and_return(related_topic)
        end

        context "when topic constains a post from the same source" do
          let(:post_with_same_source) { build(:post, source: post.source) }
          let(:related_topic) { create(:topic, posts: [post_with_same_source]) }

          it_behaves_like "creator of new topic"
        end

        context "when topic doesn't contain post from the same source" do
          it "appends post to topic" do
            subject
            expect(post.topic).to eq(related_topic)
            expect(post.main_topic).to be_blank
          end
        end
      end

      context "when there is no topic for post" do
        before do
          allow(PostsFetcher::RelatedPostsFinder)
            .to receive_message_chain(:new, :topic_with_related_posts_or_nil)
            .and_return(nil)
        end

        it_behaves_like "creator of new topic"
      end
    end
  end
end
