require "rails_helper"

RSpec.describe Posts::CategoriesUpdater do
  describe "#updated_category_names" do
    subject { described_class.new(params).updated_category_names }

    context "when there is no post for passing post id" do
      let(:params) { { post_id: "invaid_id" } }

      it "raises not found error" do
        expect { subject }.to raise_error(ActiveRecord::RecordNotFound)
      end
    end

    context "when there is a post for passing post id" do
      let(:post_category) { create(:category) }
      let(:post) { create(:post, categories: [post_category]) }
      let(:params) { { post_id: post.id, category_ids: category_ids } }

      context "when there are no categories for passing category ids" do
        let(:category_ids) { ["invalid id", nil, 404] }

        it "ignores invalid ids during update" do
          expect { subject }.to change { post.categories.count }.from(1).to(0)
        end
      end

      context "when there are categories for passing category ids" do
        let(:updating_categories) { create_list(:category, 2) }
        let(:category_ids) { updating_categories.map(&:id) }
        let(:updated_post_category_names) do
          updating_categories.map(&:name).join(", ")
        end

        it "changes post categories" do
          expect { subject }
            .to change { post.categories.count }.from(1).to(updating_categories.count)
        end

        it "returns updated post category names" do
          is_expected.to eq(updated_post_category_names)
        end
      end
    end
  end
end
