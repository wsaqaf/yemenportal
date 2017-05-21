require "rails_helper"

describe PostCreaterService do
  subject { described_class.new }

  let(:source) { create(:source) }
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
        subject.add_post(item, source)
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

        subject.add_post(item, source)

        post = Post.find_by(published_at: item.pubDate)
        expect(post.categories.to_a).to eql([])
      end
    end

    describe "(module tests)" do
      let(:post) { build :post }
      let(:whitelisted_source) { create(:source, whitelisted: true) }

      it "facebook post call save action" do
        allow(Post).to receive(:new).with(description: "description\n Go", link: "link", photo_url: "some_img",
          published_at: fb_item["created_time"], title: "description", source: fb_source, keywords: [],
          posts: []).and_return(post)
        allow(post).to receive(:categories=).with([fb_source.category]).and_return(post)

        expect(post).to receive(:save)

        subject.add_post(fb_item, fb_source)
      end

      it "post call save action" do
        allow(Post).to receive(:new).with(description: "description", link: "link", published_at: item.pubDate,
          source: source, title: item.title, photo_url: "some_path", keywords: [], posts: []).and_return(post)
        allow(post).to receive(:categories=).with([source.category]).and_return(post)

        expect(post).to receive(:save)

        subject.add_post(item, source)
      end

      it "post with approve state" do
        allow(Post).to receive(:new).with(description: "description", link: "link", published_at: item.pubDate,
          title: item.title, source: whitelisted_source, photo_url: "some_path",
          keywords: [], posts: []).and_return(post)

        subject.add_post(item, whitelisted_source)
        expect(post.state).to eql("approved")
      end

      it "not set category" do
        allow(Post).to receive(:new).with(description: "description", link: "link", published_at: item.pubDate,
          title: item.title, source: source, photo_url: "some_path", keywords: [], posts: []).and_return(post)
        allow(source).to receive(:category).and_return(nil)
        expect(post).not_to receive(:categories=)

        subject.add_post(item, source)
      end

      %i(link pubDate title).each do |field|
        it "rais error when #{field} is empty" do
          allow(item).to receive(field).and_return(nil)

          expect(source).to receive(:update).with(state: Source.state.not_full_info)
          subject.add_post(item, source)
        end
      end
    end
  end
end
