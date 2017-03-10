require "rails_helper"

describe PostCreaterService do
  let(:source) { create(:source) }

  describe "#add_post" do
    let(:item) { double(description: "description", link: "link", pubDate: Time.new, title: "title") }

    context "source has category", slow: true do
      before do
        described_class.add_post(item, source)
      end

      it "post created with item fields" do
        post = Post.find_by(published_at: item.pubDate)
        expect(post.attributes).to include("description" => item.description, "link" => item.link,
          "published_at" => item.pubDate, "source_id" => source.id, "title" => item.title)
      end

      it "post has category" do
        post = Post.find_by(published_at: item.pubDate)
        expect(post.categories).to include(source.category)
      end
    end

    context "source hasn't category", slow: true do
      it "post hasn't category too" do
        allow(source).to receive(:category).and_return(nil)

        described_class.add_post(item, source)

        post = Post.find_by(published_at: item.pubDate)
        expect(post.categories.to_a).to eql([])
      end
    end

    context "module tests" do
      let(:post) { build :post }
      let(:categories_post) { double }

      before do
        allow(Post).to receive(:new).with(description: "description", link: "link", published_at: item.pubDate,
          title: item.title, source: source).and_return(post)
      end

      it "" do
        allow(post).to receive(:categories=).with([source.category]).and_return(post)

        expect(post).to receive(:save)

        described_class.add_post(item, source)
      end

      it "not set category" do
        allow(source).to receive(:category).and_return(nil)
        expect(post).not_to receive(:categories=)

        described_class.add_post(item, source)
      end
    end
  end
end
