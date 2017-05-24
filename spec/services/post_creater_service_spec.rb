require "rails_helper"

describe PostCreaterService do
  subject(:rss_subject) { described_class.new(source) }
  subject(:fb_subject) { described_class.new(fb_source) }

  let(:source) { create(:source, source_type: :rss) }
  let(:fb_source) { create(:source, source_type: :facebook) }

  describe "#add_post" do
    let(:item) do
      double(description: "<img src='some_path'/>description", link: "link",
      pubDate: Time.new, title: "title")
    end
    let(:fb_item) do
      { "message" => "description\n Go", "link" => "link",
      "created_time" => Time.new, "picture" => "some_img" }
    end

    context "source has category", slow: true do
      before do
        rss_subject.add_post(item)
      end

      it "post created with item fields" do
        post = Post.find_by(published_at: item.pubDate)
        expect(post.attributes).to include("description" => item.description, "link" => item.link,
          "source_id" => source.id, "title" => item.title)
      end

      it "post has category" do
        post = Post.find_by(published_at: item.pubDate)
        expect(post.categories).to include(source.category)
      end
    end

    context "source hasn't category", slow: true do
      it "post hasn't category too" do
        allow(source).to receive(:category).and_return(nil)

        rss_subject.add_post(item)

        post = Post.find_by(published_at: item.pubDate)
        expect(post.categories.to_a).to eql([])
      end
    end

    describe "(module tests)" do
      subject(:whitelisted_subject) { described_class.new(whitelisted_source) }
      let(:post) { build :post }
      let(:whitelisted_source) { create(:source, whitelisted: true) }

      it "facebook post call save action" do
        allow(Post).to receive(:new).with(description: "description\n Go", link: "link", photo_url: "some_img",
          published_at: fb_item["created_time"], title: "description", source: fb_source, keywords: [],
          posts: []).and_return(post)
        allow(post).to receive(:categories=).with([fb_source.category]).and_return(post)

        expect(post).to receive(:save)

        fb_subject.add_post(fb_item)
      end

      it "post call save action" do
        allow(Post).to receive(:new).with(description: "description", link: "link", published_at: item.pubDate,
          source: source, title: item.title, photo_url: "some_path", keywords: [], posts: []).and_return(post)
        allow(post).to receive(:categories=).with([source.category]).and_return(post)

        expect(post).to receive(:save)

        rss_subject.add_post(item)
      end

      it "post with approve state" do
        allow(Post).to receive(:new).with(description: "description", link: "link", published_at: item.pubDate,
          title: item.title, source: whitelisted_source, photo_url: "some_path",
          keywords: [], posts: []).and_return(post)

        whitelisted_subject.add_post(item)
        expect(post.state).to eql("approved")
      end

      it "not set category" do
        allow(Post).to receive(:new).with(description: "description", link: "link", published_at: item.pubDate,
          title: item.title, source: source, photo_url: "some_path", keywords: [], posts: []).and_return(post)
        allow(source).to receive(:category).and_return(nil)
        expect(post).not_to receive(:categories=)

        rss_subject.add_post(item)
      end

      %i(link pubDate title).each do |field|
        it "rais error when #{field} is empty" do
          allow(item).to receive(field).and_return(nil)

          expect(source).to receive(:update).with(state: Source.state.not_full_info)
          rss_subject.add_post(item)
        end
      end
    end
  end
end
